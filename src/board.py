from typing import Self, TypeVar
from enum import StrEnum
from .gridref import GridRef

T = TypeVar('T')

# Длина ряда крестиков/ноликов для выигрыша
# в зависимости от размера клетки
WINNING_LENGTH_PER_GRID_SIZE: dict[int, int] = {
# Размер клетки: Длина
    3          : 3,
    4          : 3,
    5          : 4,
    6          : 5
}


class CellState(StrEnum):
    EMPTY = ' '
    X     = 'X'
    O     = 'O'


class BoardException(Exception):
    pass


class Board(object):
    _grid: list[list[CellState]]
    _map: list[list[GridRef]]

    @staticmethod
    def rotate45(grid: list[list[T]], reverse: bool = False) -> list[list[T]]:
        n = len(grid)
        result: list[list[T]] = [[] for _ in range(2 * n - 1)]
        for i in range(n):
            for j in range(n):
                if reverse:
                    result[i - j].append(grid[i][j])
                else:
                    result[i + j].append(grid[i][j])
        return result

    @staticmethod
    def rotate90(grid: list[list[T]]) -> list[list[T]]:
        n = len(grid)
        return [[grid[i][j] for i in range(n)] for j in range(n)]

    @staticmethod
    def find_all_lines(grid: list[list[T]], length: int) -> list[list[T]]:
        all_rows = [*grid, *Board.rotate45(grid), *Board.rotate90(grid), *Board.rotate45(grid, reverse=True)]
        for i in range(len(all_rows) - 1, -1, -1):
            if len(all_rows[i]) < length:
                all_rows.pop(i)
        result: list[list[T]] = []
        for row in all_rows:
            result += [row[i:i+length] for i in range(len(row) - length + 1)]
        return result

    def __init__(self: Self, size: int) -> None:
        if size not in [3, 4, 5, 6]:
            raise BoardException("Size must be from 3 to 6.")
        self._grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self._map = Board.find_all_lines(
            [[GridRef(j, i) for i in range(size)] for j in range(size)],
            WINNING_LENGTH_PER_GRID_SIZE[size]
        )

    def size(self: Self) -> int:
        return len(self._grid)

    def __str__(self: Self) -> str:
        result: list[str] = []
        for row in self._grid:
            result.append(' | '.join(list(map(str, row))))
        return ('\n' + '--+-' * (self.size() - 1) + '-\n').join(result)

    def is_full(self: Self) -> bool:
        for row in self._grid:
            if CellState.EMPTY in row:
                return False
        return True

    def check_for_win(self: Self) -> CellState:
        for line in self._map:
            for side in [CellState.X, CellState.O]:
                if all(cell == CellState.X for cell in list(map(GridRef.get_lambda(self._grid), line))):
                    return side
        return CellState.EMPTY

