import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReadmeTest(unittest.TestCase):
    def test_every_discount_code_is_documented(self):
        source = (ROOT / "shop" / "pricing.py").read_text()
        readme = (ROOT / "README.md").read_text()
        for code in sorted(set(re.findall(r'"([A-Z][A-Z0-9]+)"', source))):
            self.assertIn(code, readme, f"discount code {code} is not documented in README.md")
