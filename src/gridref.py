from typing import Self, TypeVar
from collections.abc import Callable

T = TypeVar('T')


class GridRef(object):
    def __init__(self: Self, i: int, j: int) -> None:
        self._i = i
        self._j = j

    def get(self: Self, grid: list[list[T]]) -> T:
        return grid[self._i][self._j]

    def set(self: Self, grid: list[list[T]], val: T) -> None:
        grid[self._i][self._j] = val

    @staticmethod
    def get_lambda(grid: list[list[T]]) -> Callable[..., T]:
        def wrapper(ref: GridRef) -> T:
            return ref.get(grid)
        return wrapper

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, GridRef):
            return NotImplemented
        return self._i == other._i and self._j == other._j

    def to_tuple(self: Self) -> tuple[int, int]:
        return (self._i, self._j)
