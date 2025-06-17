from typing import Self
from collections.abc import Callable
from enum import StrEnum


class CellState(StrEnum):
    EMPTY = ' '
    X     = 'X'
    O     = 'O'
    def opposite(self: Self):
        if self == CellState.EMPTY:
            return CellState.EMPTY
        if self == CellState.X:
            return CellState.O
        if self == CellState.O:
            return CellState.X


class CellRef(object):
    def __init__(self: Self, i: int, j: int) -> None:
        self._i = i
        self._j = j

    def get(self: Self, grid: list[list[CellState]]) -> CellState:
        return grid[self._i][self._j]

    def set(self: Self, grid: list[list[CellState]], val: CellState) -> None:
        grid[self._i][self._j] = val

    @staticmethod
    def get_lambda(grid: list[list[CellState]]) -> Callable[..., CellState]:
        def wrapper(ref: CellRef) -> CellState:
            return ref.get(grid)
        return wrapper

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, CellRef):
            return NotImplemented
        return self._i == other._i and self._j == other._j

    def to_tuple(self: Self) -> tuple[int, int]:
        return (self._i, self._j)

    def __repr__(self: Self) -> str:
        return str(self.to_tuple())
