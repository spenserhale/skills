#!/usr/bin/env python3
"""Render a modern WordPress plugin skeleton into a new directory.

Usage:
    python3 scaffold.py --slug acme-redirects --name "Acme Redirects" \\
        --namespace 'Acme\\Redirects' --vendor acme --author "Acme Inc" \\
        [--with-js] [--php 8.4] [--wp 6.9] [--dest DIR] [--dry-run]

Examples:
    # PHP-only plugin into ./acme-redirects
    python3 scaffold.py --slug acme-redirects --name "Acme Redirects" \\
        --namespace 'Acme\\Redirects' --vendor acme --author "Acme Inc"

    # With a React/TypeScript admin screen, network-wide, into a chosen folder
    python3 scaffold.py --slug acme-redirects --name "Acme Redirects" \\
        --namespace 'Acme\\Redirects' --vendor acme --author "Acme Inc" \\
        --with-js --network --dest ~/Code/WordPress/plugins/acme-redirects

Reads templates from ../assets/skeleton (and ../assets/skeleton-js with --with-js),
replaces {{TOKENS}}, renames plugin.php to <slug>.php, and generates src/classmap.php.
Refuses to write into a non-empty directory unless --force is given.
Exit codes: 0 ok, 1 bad input, 2 destination not empty.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CORE = SKILL_DIR / "assets" / "skeleton"
JS = SKILL_DIR / "assets" / "skeleton-js"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NS_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:\\[A-Z][A-Za-z0-9]*)*$")

JS_HOOKS = """
// Admin screen and its REST route (React app in resources/js, built to build/).
add_action( 'admin_menu', [ Admin\\AdminPage::class, 'register' ] );
add_action( 'admin_enqueue_scripts', [ Admin\\AdminPage::class, 'enqueue' ] );
add_action( 'rest_api_init', [ Admin\\StatusController::class, 'register' ] );
"""

CI_JS_CHECK = """
  js:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-node@v7
        with:
          node-version-file: .nvmrc
          cache: npm

      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint:js
      - run: npm run build
"""

CI_JS_BUILD = """
      - uses: actions/setup-node@v7
        with:
          node-version-file: .nvmrc
          cache: npm

      - name: Build assets
        run: npm ci && npm run build
"""

TYPE_RE = re.compile(
    r"^\s*(?:(?:final|abstract|readonly)\s+)*(?:class|interface|trait|enum)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
NS_DECL_RE = re.compile(r"^\s*namespace\s+([^;{\s]+)\s*;", re.M)


def pascal(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("-"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render a modern WordPress plugin skeleton (wp-env, PHPUnit, PHPStan max, Rector, classmap autoloader, built-branch CI).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Reads templates", 1)[0].split("Examples:", 1)[1] if "Examples:" in __doc__ else None,
    )
    p.add_argument("--slug", required=True, help="plugin folder and main file name, kebab-case (acme-redirects)")
    p.add_argument("--name", required=True, help='human name for the plugin header ("Acme Redirects")')
    p.add_argument("--namespace", required=True, help=r"root PHP namespace, single backslashes (Acme\Redirects)")
    p.add_argument("--vendor", required=True, help="Composer vendor, lowercase (acme)")
    p.add_argument("--author", required=True, help="author name for the header and composer.json")
    p.add_argument("--author-email", default="", help="author email for composer.json")
    p.add_argument("--author-uri", default="", help="Author URI header")
    p.add_argument("--description", default="", help="one-line plugin description")
    p.add_argument("--hook-prefix", default="", help="public hook prefix; default <vendor>/<slug-without-vendor> (acme/redirects)")
    p.add_argument("--text-domain", default="", help="text domain; default the slug (wp.org requires the slug)")
    p.add_argument("--php", default="8.4", help="minimum PHP, major.minor (default 8.4)")
    p.add_argument("--wp", default="6.9", help="Requires at least (default 6.9)")
    p.add_argument("--test-port", type=int, default=8889, help="port for the wp-env test environment (default 8889)")
    p.add_argument("--with-js", action="store_true", help="add a React/TypeScript admin screen built with @wordpress/scripts, plus a REST route")
    p.add_argument("--wporg", action="store_true", help="distributing on WordPress.org: omit the Update URI header (it would block wp.org updates)")
    p.add_argument("--network", action="store_true", help="add 'Network: true' (network-activated on multisite)")
    p.add_argument("--disclaimer", default="", help="third-party name for a trademark disclaimer in the header (Cloudflare, Inc.)")
    p.add_argument("--dest", default="", help="output directory (default ./<slug>)")
    p.add_argument("--force", action="store_true", help="write into a non-empty destination, overwriting files")
    p.add_argument("--dry-run", action="store_true", help="print the files that would be written and the token values, write nothing")
    return p.parse_args(argv)


def build_tokens(a: argparse.Namespace) -> dict[str, str]:
    errors = []
    if not SLUG_RE.match(a.slug):
        errors.append(f"--slug must be kebab-case a-z0-9: {a.slug!r}")
    if not NS_RE.match(a.namespace):
        errors.append(rf"--namespace must look like Vendor\Name with single backslashes: {a.namespace!r}")
    if not re.match(r"^[a-z0-9]([_.-]?[a-z0-9]+)*$", a.vendor):
        errors.append(f"--vendor must be a lowercase Composer vendor: {a.vendor!r}")
    m = re.match(r"^(\d)\.(\d)$", a.php)
    if not m:
        errors.append(f"--php must be major.minor like 8.4: {a.php!r}")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    short = a.slug[len(a.vendor) + 1:] if a.slug.startswith(a.vendor + "-") else a.slug
    hook_prefix = a.hook_prefix or f"{a.vendor}/{short}"
    const = re.sub(r"[^A-Z0-9]", "_", a.slug.upper())
    disclaimer = ""
    if a.disclaimer:
        disclaimer = (
            " *\n"
            f" * Disclaimer: This plugin is not affiliated with, endorsed by, or in any\n"
            f" * way officially connected to {a.disclaimer} Their names, trademarks, and\n"
            f" * logos are the property of their respective owners.\n"
        )

    return {
        "NAME": a.name,
        "SLUG": a.slug,
        "DESCRIPTION": a.description or a.name,
        "NAMESPACE": a.namespace,
        "NAMESPACE_JSON": a.namespace.replace("\\", "\\\\"),
        "VENDOR": a.vendor,
        "AUTHOR": a.author,
        "AUTHOR_EMAIL_JSON": f',\n            "email": {json.dumps(a.author_email)}' if a.author_email else "",
        "AUTHOR_URI_HEADER": f" * Author URI: {a.author_uri}\n" if a.author_uri else "",
        "HOOK_PREFIX": hook_prefix,
        "REST_NAMESPACE": a.slug,
        "TEXT_DOMAIN": a.text_domain or a.slug,
        "PHP_MIN": a.php,
        "PHP_ID": f"{m.group(1)}0{m.group(2)}00",
        "WP_MIN": a.wp,
        "CONST_TYPE": "string " if (int(m.group(1)), int(m.group(2))) >= (8, 3) else "",
        "YEAR": str(datetime.date.today().year),
        "CONST": const,
        "JS_GLOBAL": pascal(a.slug) + "Config",
        "TEST_PORT": str(a.test_port),
        "UPDATE_URI_HEADER": "" if a.wporg else f" * Update URI: https://github.com/{a.vendor}/{a.slug}\n",
        "NETWORK_HEADER": " * Network: true\n" if a.network else "",
        "DISCLAIMER": disclaimer,
        "JS_HOOKS": JS_HOOKS if a.with_js else "",
        "CI_JS_CHECK": CI_JS_CHECK if a.with_js else "",
        "CI_JS_BUILD": CI_JS_BUILD if a.with_js else "",
    }


def render(text: str, tokens: dict[str, str]) -> str:
    out = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: tokens.get(m.group(1), m.group(0)), text)
    left = sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", out)))
    if left:
        raise ValueError(f"unknown tokens: {', '.join(left)}")
    return out


def collect(with_js: bool) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for root in [CORE] + ([JS] if with_js else []):
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != ".DS_Store":
                files[path.relative_to(root).as_posix()] = path
    files.pop("src/classmap.php", None)  # regenerated from the rendered sources
    return files


def classmap(rendered: dict[str, str]) -> str:
    entries = {}
    for rel, text in rendered.items():
        if not rel.startswith("src/") or not rel.endswith(".php"):
            continue
        ns = NS_DECL_RE.search(text)
        for name in TYPE_RE.findall(text):
            fq = (ns.group(1) + "\\" if ns else "") + name
            entries[fq] = rel[len("src"):]
    # Byte-identical to bin/classmap.php (var_export doubles backslashes), so --check passes.
    lines = [f"\t'{k.replace(chr(92), chr(92) * 2)}' => '{v}'," for k, v in sorted(entries.items())]
    return (
        "<?php\n// Generated by bin/classmap.php. Do not edit; run `composer classmap`.\n\nreturn [\n"
        + "\n".join(lines)
        + "\n];\n"
    )


def main(argv: list[str]) -> int:
    a = parse_args(argv)
    tokens = build_tokens(a)
    dest = Path(a.dest).expanduser() if a.dest else Path.cwd() / a.slug

    rendered: dict[str, str] = {}
    for rel, src in collect(a.with_js).items():
        out_rel = f"{a.slug}.php" if rel == "plugin.php" else rel
        try:
            rendered[out_rel] = render(src.read_text(), tokens)
        except ValueError as e:
            print(f"error: {src}: {e}", file=sys.stderr)
            return 1
    rendered["src/classmap.php"] = classmap(rendered)

    if a.dry_run:
        print(json.dumps({"dest": str(dest), "tokens": {k: v for k, v in tokens.items() if "\n" not in v}, "files": sorted(rendered)}, indent=2))
        return 0

    if dest.exists() and any(dest.iterdir()) and not a.force:
        print(f"error: {dest} is not empty; pass --force to overwrite matching files", file=sys.stderr)
        return 2

    for rel, text in sorted(rendered.items()):
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    print(f"Wrote {len(rendered)} files to {dest}")
    print("Next: cd into it, then run the verify steps from the skill (composer install, composer check, wp-env tests).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
