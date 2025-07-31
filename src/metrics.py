# Offline minimal placeholder (can be extended if needed)
from time import perf_counter
from contextlib import contextmanager


def noop(*_, **__) -> None:
    pass


@contextmanager
def time_block():
    start = perf_counter()
    yield lambda: perf_counter() - start
