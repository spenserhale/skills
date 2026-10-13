import unittest

from textutil import initials, truncate


class TextutilTest(unittest.TestCase):
    def test_truncate_short_text_unchanged(self):
        self.assertEqual(truncate("hello", 10), "hello")

    def test_truncate_long_text(self):
        self.assertEqual(truncate("hello world", 6), "hello…")

    def test_initials(self):
        self.assertEqual(initials("ada lovelace"), "AL")
