from typing import Self, TypeVar

T = TypeVar('T')


class GridRef(object):
    _i: int
    _j: int

    def __init__(self: Self, i: int, j: int):
        self._i = i
        self._j = j

    def get(self: Self, grid: list[list[T]]) -> T:
        return grid[self._i][self._j]

    def set(self: Self, grid: list[list[T]], val: T) -> None:
        grid[self._i][self._j] = val

    @staticmethod
    def get_lambda(grid: list[list[T]]):
        def wrapper(ref: GridRef) -> T:
            return ref.get(grid)
        return wrapper

    @staticmethod
    def set_lambda(grid: list[list[T]], val: T):
        def wrapper(ref: GridRef) -> None:
            ref.set(grid, val)
        return wrapper
