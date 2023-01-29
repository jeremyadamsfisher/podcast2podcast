import time
from contextlib import contextmanager

import requests
from loguru import logger


@contextmanager
def yap(about):
    """Yap about something."""
    tick = time.time()
    logger.info("Starting {}...", about)
    yield
    tock = time.time()
    logger.info("...done {}. ({:.2f}s elapsed.)", about, tock - tick)


def download_file(url, fp_out):
    """Download a file from a given URL."""
    with requests.get(url, stream=True) as r, open(fp_out, "wb") as f:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def retry(n=3, delay=5):
    """Retry a function n times with exponential backoff."""

    def inner(f):
        def wrapper(*args, **kwargs):
            e_prev = None
            for i in range(n):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        "failed on try {}: {}\n{}", i + 1, e, e.__traceback__
                    )
                    logger.info("waiting for {} seconds", delay ** (i + 1))
                    time.sleep(delay ** (i + 1))
                    e_prev = e
            raise e_prev

        return wrapper

    return inner
