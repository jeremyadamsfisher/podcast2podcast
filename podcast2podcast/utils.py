import time
from contextlib import contextmanager

from loguru import logger


@contextmanager
def yap(about):
    """Yap about something."""
    tick = time.time()
    logger.info("Starting {}...", about)
    yield
    tock = time.time()
    logger.info("...done {}. ({:.2f}s elapsed.)", about, tock - tick)
