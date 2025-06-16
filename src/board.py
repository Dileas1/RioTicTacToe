from typing import Self, TypeVar
from .cells import CellRef, CellState
from collections.abc import Callable

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


class BoardException(Exception):
    pass


class Board(object):
    _grid: list[list[CellState]]
    _map: list[list[CellRef]]
    _weights: dict[tuple[int, int], int]


# /////////////////////////////////////////
# --- Вспомогательные методы --------------
# /////////////////////////////////////////


    @staticmethod
    def __rotate45(grid: list[list[T]], reverse: bool = False) -> list[list[T]]:
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
    def __rotate90(grid: list[list[T]]) -> list[list[T]]:
        n = len(grid)
        return [[grid[i][j] for i in range(n)] for j in range(n)]

    @staticmethod
    def __find_all_lines(grid: list[list[T]], length: int) -> list[list[T]]:
        all_rows = [*grid, *Board.__rotate45(grid), *Board.__rotate90(grid), *Board.__rotate45(grid, reverse=True)]
        for i in range(len(all_rows) - 1, -1, -1):
            if len(all_rows[i]) < length:
                all_rows.pop(i)
        result: list[list[T]] = []
        for row in all_rows:
            result += [row[i:i+length] for i in range(len(row) - length + 1)]
        return result

    @staticmethod
    def __generate_ref_grid(size: int) -> list[list[CellRef]]:
        return [[CellRef(j, i) for i in range(size)] for j in range(size)]

    def __ref2state(self: Self, row: list[CellRef]) -> list[CellState]:
        return list(map(CellRef.get_lambda(self._grid), row))

    def _get_weight(self: Self, ref: CellRef) -> int:
        return self._weights[ref.to_tuple()]


# /////////////////////////////////////////
# --- Встроенные методы -------------------
# /////////////////////////////////////////


    def __init__(self: Self, size: int) -> None:
        if size not in [3, 4, 5, 6]:
            raise BoardException("Size must be from 3 to 6.")
        self._grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self._map = Board.__find_all_lines(Board.__generate_ref_grid(size), WINNING_LENGTH_PER_GRID_SIZE[size])
        reflist: list[CellRef] = []
        for row in Board.__generate_ref_grid(size):
            reflist += row
        self._weights = {}
        for ref in reflist:
            count_func: Callable[[list[CellRef]], int] = lambda l: l.count(ref)
            self._weights[ref.to_tuple()] = sum(list(map(count_func, self._map)))

    def __str__(self: Self) -> str:
        result: list[str] = []
        for row in self._grid:
            result.append(' | '.join(list(map(str, row))))
        return ('\n' + '--+-' * (self.size() - 1) + '-\n').join(result)

    def size(self: Self) -> int:
        return len(self._grid)


# /////////////////////////////////////////
# --- Анализ игры  ------------------------
# /////////////////////////////////////////


    def is_full(self: Self) -> bool:
        for row in self._grid:
            if CellState.EMPTY in row:
                return False
        return True

    def check_for_win(self: Self) -> CellState:
        for row in self._map:
            for side in [CellState.X, CellState.O]:
                if all(cell == side for cell in self.__ref2state(row)):
                    return side
        return CellState.EMPTY

    def check_for_immediate_wins(self: Self) -> dict[CellState, list[CellRef]]:
        result: dict[CellState, list[CellRef]] = {
            CellState.X: [],
            CellState.O: []
        }
        for row in self._map:
            for side in [CellState.X, CellState.O]:
                if self.__ref2state(row).count(side) == len(row) - 1:
                    for ref in row:
                        if ref.get(self._grid) == CellState.EMPTY:
                            result[side].append(ref)
        return result

