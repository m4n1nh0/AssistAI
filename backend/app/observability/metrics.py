from time import perf_counter
from typing import Callable, TypeVar

T = TypeVar("T")


def measure_duration(callback: Callable[[], T]) -> tuple[T, float]:
    start = perf_counter()
    result = callback()
    return result, perf_counter() - start
