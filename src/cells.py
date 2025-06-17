from typing import Self, TypeVar
from collections.abc import Callable
from enum import StrEnum

T = TypeVar("T")


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

    def __hash__(self: Self):
        return hash(self.to_tuple())

    @classmethod
    def generate_grid(cls: type[Self], size: int) -> list[list[Self]]:
        return [[cls(j, i) for i in range(size)] for j in range(size)]

    @classmethod
    def generate_list(cls: type[Self], size: int) -> list[Self]:
        ref_grid = cls.generate_grid(size)
        all_cells: list[Self] = []
        for row in ref_grid:
            all_cells += row
        return all_cells

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

    @classmethod
    def map_out_all_wins(cls: type[Self], grid_size: int, win_length: int) -> list[list[Self]]:
        grid = cls.generate_grid(grid_size)
        all_rows = [*grid, *cls.__rotate45(grid), *cls.__rotate90(grid), *cls.__rotate45(grid, reverse=True)]
        for i in range(len(all_rows) - 1, -1, -1):
            if len(all_rows[i]) < win_length:
                all_rows.pop(i)
        result: list[list[Self]] = []
        for row in all_rows:
            result += [row[i:i+win_length] for i in range(len(row) - win_length + 1)]
        return result


class CellWeightMap(dict[CellRef, int]):
    __size: int = 0
    __win_length: int = 0

    def __init__(self: Self, size: int = 0, win_length: int = 0):
        if size < 3 or win_length < 3:
            return
        self.__size = size
        self.__win_length = win_length
        reflist: list[CellRef] = CellRef.generate_list(self.__size)
        win_map = CellRef.map_out_all_wins(self.__size, self.__win_length)
        for ref in reflist:
            count_func: Callable[[list[CellRef]], int] = lambda l: l.count(ref)
            self[ref] = sum(list(map(count_func, win_map)))

    def __new__(cls: type[Self], size: int = 0, win_length: int = 0) -> Self:
        if not hasattr(cls, 'instance') or cls.instance.__size != size or cls.instance.__win_length != win_length:
            cls.instance = super(CellWeightMap, cls).__new__(cls, size, win_length)
        return cls.instance
