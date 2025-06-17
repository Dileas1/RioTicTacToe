from typing import Self, TypeVar
from .cells import CellRef, CellState
from collections.abc import Callable
import random

T = TypeVar('T')


class BoardException(Exception):
    pass


class Board(object):
    __grid: list[list[CellState]]
    __map: list[list[CellRef]]
    __weights: dict[tuple[int, int], int]
    __cpu_side: CellState

    def size(self: Self) -> int:
        return len(self.__grid)


# /////////////////////////////////////////
# --- Вспомогательные методы --------------
# /////////////////////////////////////////

    @staticmethod
    def __get_win_condition(size: int) -> int:
        if size < 3:
            return 0
        if size in [3, 4]:
            return 3
        if size == 5:
            return 4
        else:
            return 5

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

    @staticmethod
    def __generate_ref_list(size: int) -> list[CellRef]:
        ref_grid = Board.__generate_ref_grid(size)
        all_cells: list[CellRef] = []
        for row in ref_grid:
            all_cells += row
        return all_cells

    @staticmethod
    def __split_list(l: list[T], n: int) -> list[list[T]]:
        result: list[list[T]] = []
        for k in range(n, len(l) + 1):
            result += [l[i:i+k] for i in range(len(l)-k+1)]
        return result

    def __ref2state(self: Self, row: list[CellRef]) -> list[CellState]:
        return list(map(CellRef.get_lambda(self.__grid), row))

    def __can_complete_line(self: Self, row: list[CellRef], side: CellState) -> bool:
        data = self.__ref2state(row)
        return all([
            data.count(side) == len(data) - 1,
            data.count(side.opposite()) == 0,
            data.count(CellState.EMPTY) == 1
        ])

    def __find_empty_cells(self: Self, row: list[CellRef]) -> list[CellRef]:
        data = self.__ref2state(row)
        indices: list[int] = []
        for i in range(len(data)):
            if data[i] == CellState.EMPTY:
                indices.append(i)
        result = [row[i] for i in indices]
        return result

    def __get_weight(self: Self, ref: CellRef) -> int:
        return self.__weights[ref.to_tuple()]

    def __get_all_legal_moves(self: Self) -> list[CellRef]:
        return self.__find_empty_cells(Board.__generate_ref_list(self.size()))

    def __make_a_move(self: Self, ref: CellRef, side: CellState) -> bool:
        try:
            if ref.get(self.__grid) == CellState.EMPTY:
                ref.set(self.__grid, side)
                return True
        except:
            pass
        return False


# /////////////////////////////////////////
# --- Встроенные методы -------------------
# /////////////////////////////////////////


    def __init__(self: Self, size: int) -> None:
        if size < 3:
            raise BoardException("Size must be 3 or larger.")
        self.__grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.__map = Board.__find_all_lines(Board.__generate_ref_grid(size), Board.__get_win_condition(size))
        reflist: list[CellRef] = []
        for row in Board.__generate_ref_grid(size):
            reflist += row
        self.__weights = {}
        for ref in reflist:
            count_func: Callable[[list[CellRef]], int] = lambda l: l.count(ref)
            self.__weights[ref.to_tuple()] = sum(list(map(count_func, self.__map)))
        self.__cpu_side = CellState.O

    def __str__(self: Self) -> str:
        result: list[str] = []
        for row in self.__grid:
            result.append(' | '.join(list(map(str, row))))
        return ('\n' + '--+-' * (self.size() - 1) + '-\n').join(result)


# /////////////////////////////////////////
# --- Анализ игры  ------------------------
# /////////////////////////////////////////


    def __immediate_wins(self: Self, pov: CellState = CellState.EMPTY) -> dict[CellState, list[CellRef]]:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        result: dict[CellState, list[CellRef]] = {
            pov.opposite(): [],
            pov: []
        }
        for row in self.__map:
            for side in [pov.opposite(), pov]:
                rowdata = self.__ref2state(row)
                if rowdata.count(side) == len(row) - 1:
                    try:
                        result[side].append(row[rowdata.index(CellState.EMPTY)])
                    except:
                        pass
        return result

    def __longest_possible_lines(self: Self, pov: CellState = CellState.EMPTY) -> dict[CellState, tuple[int, list[CellRef]]]:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        result: dict[CellState, tuple[int, list[CellRef]]] = {
            pov.opposite(): (0, []),
            pov: (0, [])
        }
        for side in [pov.opposite(), pov]:
            for row in self.__map:
                for chunk in Board.__split_list(row, max(2, result[side][0])):
                    if self.__can_complete_line(chunk, side):
                        cells = self.__find_empty_cells(chunk)
                        if len(cells) == 1:
                            if len(chunk) == result[side][0]:
                                result[side][1].append(cells[0])
                            elif len(chunk) > result[side][0]:
                                result[side] = (len(chunk), [cells[0]])
        return result


# /////////////////////////////////////////
# --- Функции рандомного выбора хода  -----
# /////////////////////////////////////////


    # Абсолютно рандомный ход
    def __random_move(self: Self, movelist: list[CellRef] = []) -> CellRef:
        if len(movelist) == 0:
            movelist = self.__get_all_legal_moves()
        return random.choice(movelist)

    # Рандомный из самых выгодных
    def __best_value_move(self: Self, movelist: list[CellRef] = []) -> CellRef:
        if len(movelist) == 0:
            movelist = self.__get_all_legal_moves()
        weights = list(map(self.__get_weight, movelist))
        return random.choice([movelist[k] for k in [i for i, val in enumerate(weights) if val == max(weights)]])

    # Что-то среднее
    def __hesitant_move(self: Self, movelist: list[CellRef] = []) -> CellRef:
        return random.choice([self.__random_move, self.__best_value_move])(movelist)


# /////////////////////////////////////////
# --- Функции выбора стратегии  -----------
# /////////////////////////////////////////


    def __detect_wins(self: Self, pov: CellState = CellState.EMPTY) -> list[CellRef]:
        wins = self.__immediate_wins(pov)
        for side in [pov, pov.opposite()]:
            if len(wins[side]) != 0:
                return wins[side]
        return []

    def __block_or_push(self: Self, pov: CellState = CellState.EMPTY) -> list[CellRef]:
        lines = self.__longest_possible_lines(pov)
        if lines[pov.opposite()][0] == 0 and lines[pov][0] == 0:
            return []
        if lines[pov.opposite()][0] == lines[pov][0]:
            return lines[pov.opposite()][1] + lines[pov][1]
        if lines[pov.opposite()][0] > lines[pov][0]:
            return lines[pov.opposite()][1]
        return lines[pov][1]

    def __pick_best_moves(self: Self, go_easy: bool = False, pov: CellState = CellState.EMPTY) -> list[CellRef]:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        wins = self.__detect_wins(pov)
        if (random.choice([True, False]) if go_easy else True) and (len(wins) != 0):
            return wins
        decisions = self.__block_or_push(pov)
        if (random.choice([True, False]) if go_easy else True) :
            return decisions
        return []


# /////////////////////////////////////////
# --- Публичные функции  ------------------
# /////////////////////////////////////////


    def pick_cpu_side(self: Self, side: CellState) -> None:
        if side != CellState.EMPTY:
            self.__cpu_side = side

    def is_full(self: Self) -> bool:
            for row in self.__grid:
                if CellState.EMPTY in row:
                    return False
            return True

    def check_for_win(self: Self, pov: CellState = CellState.EMPTY) -> CellState:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        for row in self.__map:
            for side in [pov, pov.opposite()]:
                if all(cell == side for cell in self.__ref2state(row)):
                    return side
        return CellState.EMPTY

    def player_move(self: Self, move: CellRef) -> bool:
        return self.__make_a_move(move, self.__cpu_side.opposite())

    def cpu_move(self: Self, move: CellRef) -> bool:
        return self.__make_a_move(move, self.__cpu_side)


# /////////////////////////////////////////
# --- Ходы ИИ в зависимости от сложности  -
# /////////////////////////////////////////


    # Лёгкая сложность - просто рандомные ходы
    def easy_diff_move(self: Self) -> CellRef:
        return self.__hesitant_move()

    def medium_diff_move(self: Self) -> CellRef:
        return self.__hesitant_move(self.__pick_best_moves(True))

    # "Мастер ничей"
    def drawmaster_diff_move(self: Self) -> CellRef:
        return self.__best_value_move(self.__pick_best_moves())
