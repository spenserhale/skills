#!/usr/bin/env python3
"""Pull the brand facts a pitch needs from a site or a local HTML file: title, description, headings,
most-used colours (as hex, converting rgb() and oklch()), fonts, and logo candidates.

usage: extract_brand.py URL_OR_FILE [--json] [--max-css 6]

Reads the page and up to --max-css linked stylesheets (same origin or relative), then reports:
  title, description, og tags, theme-color, h1-h3 headings (first 25)
  colors: top hex values by frequency, grouped by role when CSS variables are named bg/background,
          text/fg, accent/primary/brand; otherwise the most-used saturated colour is offered as the accent
  fonts: Google Fonts families and their stylesheet URLs (pass to render_card.py --font-css), plus
         font-family declarations by frequency with var() chains resolved
  logos: <img> or inline <svg> whose src, alt, or class mentions logo
Stdlib only; no JavaScript is executed, so a client-rendered app returns little: point it at the
built CSS or a saved page instead. Colours it cannot parse are listed under "unparsed".
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128.0 Safari/537.36 video-pitch/1.0"


def die(msg: str) -> None:
    print(f"extract_brand: {msg}", file=sys.stderr)
    sys.exit(1)


def read(src: str, base: str | None = None) -> tuple[str, str]:
    """Return (text, resolved_url_or_path)."""
    if base and not re.match(r"^[a-z]+:", src) and not Path(src).is_absolute():
        src = urllib.parse.urljoin(base, src) if re.match(r"^https?://", base) else str(Path(base).parent / src)
    if re.match(r"^https?://", src):
        req = urllib.request.Request(src, headers={"User-Agent": UA, "Accept": "text/html,text/css,*/*"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace"), r.geturl()
    p = Path(src)
    if not p.exists():
        raise FileNotFoundError(src)
    return p.read_text(encoding="utf-8", errors="replace"), str(p)


# ---------------------------------------------------------------- colour parsing

def clamp(x: float) -> int:
    return max(0, min(255, int(round(x))))


def hex_norm(h: str) -> str:
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h[:7]


def oklch_to_hex(L: float, C: float, H: float) -> str:
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def gamma(x: float) -> float:
        x = max(0.0, min(1.0, x))
        return 1.055 * x ** (1 / 2.4) - 0.055 if x > 0.0031308 else 12.92 * x
    return "#%02x%02x%02x" % (clamp(gamma(r) * 255), clamp(gamma(g) * 255), clamp(gamma(bb) * 255))


def hsl_to_hex(h: float, s: float, l: float) -> str:
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
    return "#%02x%02x%02x" % (clamp((r + m) * 255), clamp((g + m) * 255), clamp((b + m) * 255))


def num(s: str) -> float:
    s = s.strip()
    if s.endswith("%"):
        return float(s[:-1]) / 100
    if s.endswith("deg"):
        return float(s[:-3])
    return float(s)


def parse_colour(token: str) -> str | None:
    t = token.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}|#[0-9a-f]{6}|#[0-9a-f]{8}", t):
        return hex_norm(t)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+%?)[\s,]+([\d.]+%?)[\s,]+([\d.]+%?)(?:[\s,/]+[\d.%]+)?\s*\)", t)
    if m:
        vals = [num(v) * (255 if v.endswith("%") else 1) for v in m.groups()]
        return "#%02x%02x%02x" % tuple(clamp(v) for v in vals)
    m = re.fullmatch(r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:[\s,/]+[\d.%]+)?\s*\)", t)
    if m:
        return hsl_to_hex(float(m.group(1)), float(m.group(2)), float(m.group(3)))
    m = re.fullmatch(r"oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.]+)(?:deg)?(?:\s*/\s*[\d.%]+)?\s*\)", t)
    if m:
        L = num(m.group(1))
        C = num(m.group(2)) * (0.4 if m.group(2).endswith("%") else 1)
        return oklch_to_hex(L, C, float(m.group(3)))
    return None


COLOUR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|(?:rgba?|hsla?|oklch)\([^)]*\)")
VAR_RE = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;}]+)")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)


def role_for(name: str) -> str | None:
    n = name.lower()
    for role, keys in (("background", ("bg", "background", "surface", "canvas")),
                       ("text", ("text", "fg", "foreground", "ink")),
                       ("accent", ("accent", "primary", "brand", "highlight"))):
        if any(k in n for k in keys):
            return role
    return None


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="http(s) URL or path to an HTML file")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max-css", type=int, default=6)
    args = ap.parse_args()

    try:
        html, base = read(args.source)
    except Exception as e:  # noqa: BLE001
        die(f"cannot read {args.source}: {e}")

    pick = lambda rx: (m.group(1).strip() if (m := re.search(rx, html, re.I | re.S)) else None)  # noqa: E731
    meta = {
        "title": pick(r"<title[^>]*>(.*?)</title>"),
        "description": pick(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)') or
                       pick(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']'),
        "og_title": pick(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)'),
        "og_description": pick(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)'),
        "theme_color": pick(r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']([^"\']*)'),
    }
    headings = [strip_tags(m.group(2)) for m in re.finditer(r"<h([1-3])[^>]*>(.*?)</h\1>", html, re.I | re.S)]
    headings = [h for h in headings if h and len(h) < 160][:25]

    css_blobs = [m.group(1) for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.I | re.S)]
    inline_styles = " ".join(m.group(1) for m in re.finditer(r'style=["\']([^"\']*)', html))
    sheets = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html, re.I)
    sheets += [h for h in re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\']', html, re.I) if h not in sheets]
    google_fonts, font_css, fetched = [], [], []
    for href in sheets:
        if "fonts.googleapis.com" in href:
            fam = re.findall(r"family=([^&]+)", href)
            google_fonts += [urllib.parse.unquote(f).replace("+", " ").split(":")[0] for f in fam]
            font_css.append(href.replace("&amp;", "&"))
            continue
        if len(fetched) >= args.max_css:
            break
        try:
            css, _ = read(href, base)
            css_blobs.append(css)
            fetched.append(href)
        except Exception:  # noqa: BLE001
            continue
    css = "\n".join(css_blobs)

    counts: Counter[str] = Counter()
    unparsed: Counter[str] = Counter()
    for tok in COLOUR_RE.findall(css + " " + inline_styles):
        h = parse_colour(tok)
        (counts if h else unparsed)[h or tok] += 1
    roles: dict[str, list[str]] = {}
    for name, value in VAR_RE.findall(css):
        role = role_for(name)
        h = next((parse_colour(t) for t in COLOUR_RE.findall(value) if parse_colour(t)), None)
        if role and h:
            roles.setdefault(role, [])
            if h not in roles[role]:
                roles[role].append(h)
    variables = {name: value.strip() for name, value in VAR_RE.findall(css)}
    # Role fallback: when no variable is named like an accent, the most-used saturated colour that is
    # not a background or text colour is the best guess; say so in the output.
    def saturation(h: str) -> float:
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        mx, mn = max(r, g, b), min(r, g, b)
        return 0.0 if mx == 0 else (mx - mn) / mx
    taken = set(roles.get("background", []) + roles.get("text", []))
    if "accent" not in roles:
        guess = next((h for h, _ in counts.most_common(12) if h not in taken and saturation(h) > 0.5), None)
        if guess:
            roles["accent (guessed: most-used saturated colour)"] = [guess]
    fonts = Counter()
    for decl in FONT_RE.findall(css):
        for _ in range(4):  # resolve var(--x) chains
            m = re.match(r"var\(--([a-zA-Z0-9_-]+)", decl.strip())
            if not m or m.group(1) not in variables:
                break
            decl = variables[m.group(1)]
        first = decl.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var("):
            fonts[first] += 1
    logos = []
    for m in re.finditer(r"<img[^>]+>", html, re.I):
        tag = m.group(0)
        if re.search(r"logo", tag, re.I):
            src = re.search(r'src=["\']([^"\']+)', tag)
            if src:
                logos.append(src.group(1))
    if re.search(r"<svg[^>]*(?:class|id|aria-label)=[\"'][^\"']*logo", html, re.I):
        logos.append("(inline svg with a logo class; copy it from the page)")

    result = {
        "source": base, **meta, "headings": headings,
        "colors": [{"hex": h, "count": n} for h, n in counts.most_common(12)],
        "roles": roles, "unparsed": [t for t, _ in unparsed.most_common(5)],
        "google_fonts": list(dict.fromkeys(google_fonts)), "font_css": list(dict.fromkeys(font_css)),
        "fonts": [{"family": f, "count": n} for f, n in fonts.most_common(6)],
        "logos": logos[:5], "stylesheets_read": fetched,
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"title:        {result['title']}")
    print(f"description:  {result['description'] or result['og_description'] or '(none)'}")
    if result["theme_color"]:
        print(f"theme-color:  {result['theme_color']}")
    print("headings:     " + " | ".join(headings[:8]))
    print("colors:       " + ", ".join(f"{c['hex']} x{c['count']}" for c in result["colors"]))
    for role, hs in roles.items():
        print(f"  {role:<11} {', '.join(hs[:4])}")
    print("  (for cards: --bg first background, --bg2 a lighter or second background, --accent the accent)")
    if unparsed:
        print("unparsed:     " + ", ".join(result["unparsed"]))
    if google_fonts:
        print("google fonts: " + ", ".join(result["google_fonts"]))
        for u in result["font_css"]:
            print(f"  --font-css  {u}")
    print("font-family:  " + ", ".join(f"{f['family']} x{f['count']}" for f in result["fonts"]))
    if logos:
        print("logos:        " + ", ".join(result["logos"]))
    print(f"stylesheets:  {len(fetched)} read")


if __name__ == "__main__":
    main()
