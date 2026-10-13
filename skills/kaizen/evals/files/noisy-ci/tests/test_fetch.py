import unittest

from reportgen.fetch import fetch_with_retry


class FetchWithRetryTest(unittest.TestCase):
    def test_retries_then_succeeds(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("down")
            return ["row"]

        self.assertEqual(fetch_with_retry(flaky), ["row"])
        self.assertEqual(len(calls), 3)

    def test_gives_up_after_all_attempts(self):
        def always_down():
            raise ConnectionError("down")

        with self.assertRaises(ConnectionError):
            fetch_with_retry(always_down)

    def test_returns_first_success(self):
        self.assertEqual(fetch_with_retry(lambda: ["row"]), ["row"])
