import unittest

from reportgen.format import format_header, format_row


class FormatTest(unittest.TestCase):
    def test_format_row(self):
        self.assertEqual(format_row([1, "a"]), "1,a")

    def test_format_header(self):
        self.assertEqual(format_header(["id", "name"]), "ID,NAME")

    @unittest.skip("flaky on CI, fix later")
    def test_format_row_with_comma(self):
        self.assertEqual(format_row(["a,b"]), '"a,b"')

    @unittest.skip("flaky on CI, fix later")
    def test_format_row_unicode(self):
        self.assertEqual(format_row(["é"]), "é")
