import os
import tempfile
import unittest

from reportgen.export import report_name, write_report


class ExportTest(unittest.TestCase):
    def test_write_report_counts_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "out.csv")
            self.assertEqual(write_report(path, ["id"], [[1], [2]]), 2)

    def test_report_name_pads_day(self):
        self.assertEqual(report_name("sales", 7), "sales-07.csv")
