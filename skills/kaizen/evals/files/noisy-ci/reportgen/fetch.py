"""Fetch rows with retries."""
import time


def fetch_with_retry(fetch, attempts=3, delay=1.5):
    """Call fetch until it succeeds, sleeping between attempts."""
    # TODO: exponential backoff
    last_error = None
    for attempt in range(attempts):
        try:
            return fetch()
        except ConnectionError as error:
            last_error = error
            if attempt < attempts - 1:
                time.sleep(delay)
    raise last_error
