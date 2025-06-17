from typing import Self, TypeVar
from .cells import CellRef, CellState, CellWeightMap
import random
import copy

T = TypeVar('T')


class BoardException(Exception):
    pass


__weight_map = CellWeightMap()


class Board(object):
    __grid: list[list[CellState]]
    __map: list[list[CellRef]]
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
        global __weight_map
        return __weight_map[ref]

    def __get_all_legal_moves(self: Self) -> list[CellRef]:
        return self.__find_empty_cells(CellRef.generate_list(self.size()))

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
        win_condition = Board.__get_win_condition(size)
        self.__grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.__map = CellRef.map_out_all_wins(size, win_condition)
        global __weight_map
        __weight_map = CellWeightMap(size, win_condition)
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

    def __pick_best_moves(self: Self, pov: CellState = CellState.EMPTY, go_easy: bool = False) -> list[CellRef]:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        wins = self.__detect_wins(pov)
        if (random.choice([True, False]) if go_easy else True) and (len(wins) != 0):
            return wins
        decisions = self.__block_or_push(pov)
        if (random.choice([True, False]) if go_easy else True) :
            return decisions
        return []

    def __simulate_move(self: Self, side: CellState, move: CellRef) -> Self:
        board = copy.deepcopy(self)
        board.__make_a_move(move, side)
        return board

    def __calculate_ahead(self: Self, turns: int, board: Self | None = None, pov: CellState = CellState.EMPTY) -> dict[CellRef, object | CellState | None] | None:
        if pov == CellState.EMPTY:
            pov = self.__cpu_side
        if turns <= 0:
            return None
        if board is None:
            board = copy.deepcopy(self)
        moveset = board.__pick_best_moves(pov)
        result: dict[CellRef, object | CellState] = {}
        for move in moveset:
            outcome = board.__simulate_move(pov, move)
            has_anyone_won = outcome.check_for_win()
            if has_anyone_won != CellState.EMPTY:
                result[move] = has_anyone_won
            elif outcome.is_full():
                result[move] = self.__cpu_side.opposite()
            else:
                result[move] = (
                    self.__get_weight(move),
                    self.__calculate_ahead(turns - 1, outcome, pov.opposite())
                )
        return result

    def __assess_predictions(self: Self, predictions: dict[CellRef, object | CellState | None] | None) -> dict[CellRef, dict[str, int]] | None:
        if predictions is None:
            return None
        result: dict[CellRef, dict[str, int]] = {}
        for move in predictions:
            prediction = predictions[move]
            if prediction is None:
                continue
            if move not in result:
                result[move] = {
                    "wins": 0,
                    "total_value": self.__get_weight(move)
                }
            if isinstance(prediction, CellState):
                if prediction == self.__cpu_side:
                    result[move]["wins"] += 1
                else:
                    result[move]["wins"] -= 1
            if isinstance(prediction, dict):
                look_forward = self.__assess_predictions(prediction) # type: ignore
                if look_forward is not None:
                    for move2 in look_forward:
                        result[move]["wins"] += look_forward[move2]["wins"]
                        result[move]["total_value"] += look_forward[move2]["total_value"]
        return result

    def __gigabrain(self: Self, turns: int) -> list[CellRef]:
        simulation_results = self.__assess_predictions(self.__calculate_ahead(turns))
        if simulation_results is None:
            return []
        best_moves: list[tuple[CellRef, int, int]] = []
        for move in simulation_results:
            raw = simulation_results[move]
            outcome = (move, raw["wins"], raw["total_value"])
            if len(best_moves) == 0:
                best_moves.append(outcome)
            for best_move in best_moves:
                if (outcome[1] > best_move[1]) or (outcome[1] == best_move[1] and outcome[2] > best_move[2]):
                    best_moves = [outcome]
                    break
                if outcome[1] == best_move[1] and outcome[2] == best_move[2]:
                    best_moves.append(outcome)
                    break
        result: list[CellRef] = []
        for best_move in best_moves:
            result.append(best_move[0])
        return result


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

    def check_for_win(self: Self) -> CellState:
        for row in self.__map:
            for side in [self.__cpu_side, self.__cpu_side.opposite()]:
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

    # "Мастер ничей" - почти невозможно обыграть, я пробовал
    def drawmaster_diff_move(self: Self) -> CellRef:
        return self.__best_value_move(self.__pick_best_moves())

    # Лёгкая сложность - по большей части рандомные ходы
    def easy_diff_move(self: Self) -> CellRef:
        return self.__hesitant_move()

    # Средняя сложность - как "мастер ничей", только поддаётся в 50% случаев
    def medium_diff_move(self: Self) -> CellRef:
        return self.__hesitant_move(self.__pick_best_moves(go_easy=True))

    def hard_diff_move(self: Self) -> CellRef:
        depth = 3
        match self.size():
            case 3: depth = 9
            case 4: depth = 5
            case 5: depth = 4
            case _: pass
        return self.__best_value_move(self.__gigabrain(depth))
