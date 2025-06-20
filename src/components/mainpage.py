from typing import Self, Literal
from ..board import Diff, Board
from ..cells import CellRef, CellState
from enum import StrEnum
from threading import Lock, Thread #type: ignore
from .cell import Cell
import rio
import functools


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    def opposite(self: Self):
        if self == Theme.LIGHT:
            return Theme.DARK
        return Theme.LIGHT



class MainPage(rio.Component):
    _diff: Diff = Diff.EASY
    _size: int = 3
    _start: bool = False
    _board: Board | None = None
    _winner: CellState | None = None
    _theme: Theme = Theme.DARK
    _turn: Literal[CellState.X, CellState.O] = CellState.X

    def get_board(self: Self) -> Board:
        if self._board is None:
            self._board = Board(self._size)
        return self._board

    def reset_board(self: Self) -> None:
        self._board = None
        self._winner = None
        self._start = False
        self._turn = CellState.X

    def game_start(self: Self) -> None:
        self._start = True

    def make_selector(self: Self) -> rio.Component:
        return rio.Card(
            rio.Column(
                rio.Dropdown(
                    label="Difficulty",
                    options=[Diff.EASY, Diff.MED, Diff.HARD],
                    selected_value=self._diff,
                    on_change=lambda v: setattr(self, "_diff", v.value)),
                rio.Dropdown(
                    label="Grid Size",
                    options=[3, 4, 5, 6],
                    selected_value=self._size,
                    on_change=lambda v: setattr(self, "_size", v.value)),
                rio.Button("Play", on_press=lambda: self.game_start()),
            align_x=0.5,
            align_y=0.2,
            min_width=30
        ))

    def cpu_move(self: Self) -> None:
        board = self.get_board()
        board.cpu_move(self._diff)
        self._winner = board.detect_wins_or_draws()
        self._turn = CellState.X
        self.force_refresh()

    async def on_cell_press(self: Self, ref: CellRef) -> None:
        if self._winner is not None or self._turn is CellState.O:
            return
        board = self.get_board()
        board.player_move(ref)
        self.force_refresh()
        self._winner = board.detect_wins_or_draws()
        self.force_refresh()
        if self._winner is not None:
            return
        self._turn = CellState.O
        self.force_refresh()
        self.cpu_move()

    def make_grid(self: Self) -> rio.Component:
        ref_grid = CellRef.generate_grid(self._size)
        field: list[list[rio.Component]] = []
        win = None
        if self._board is not None:
            win = self._board.explain_win()
        for row in ref_grid:
            field.append([
                Cell(
                    get_board=self.get_board,
                    on_press=functools.partial(self.on_cell_press, ref),
                    ref=ref,
                    dim=False,
                    highlight=False if (win is None) or (ref not in win) else True
                ) for ref in row
            ])
        return rio.Grid(
            *field,
            row_spacing=1,
            column_spacing=1,
            align_x=0.5
        )

    def make_game_screen(self: Self) -> rio.Component:
        grid = self.make_grid()
        text = "Your turn!"
        if self._winner is not None:
            if self._winner == CellState.X:
                text = "You win!"
            elif self._winner == CellState.EMPTY:
                text = "It's a draw."
            else:
                text = "You lose."
        if self._turn == CellState.O:
            text = "Thinking..."
        return rio.Column(
            grid,
            rio.Text(text, align_x=0.5),
            rio.Button(
                "Return",
                icon="material/arrow_back",
                style="colored-text",
                on_press=lambda: self.reset_board(),
            ),
            spacing=2,
            margin=2,
            align_x=0.5,
            align_y=0.2,
        )


    def build(self: Self) -> rio.Component:
        if not self._start:
            return self.make_selector()
        return self.make_game_screen()
