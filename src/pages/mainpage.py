from typing import Self
from ..board import Diff, Board
from ..cells import CellRef, CellState
from enum import StrEnum
from threading import Lock
from .. import components as comps
import rio
import functools


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    def opposite(self: Self):
        if self == Theme.LIGHT:
            return Theme.DARK
        return Theme.LIGHT
    def get_settings(self: Self) -> rio.Theme:
        return rio.Theme.from_colors(
            primary_color=rio.Color.from_hex("01dffdff"),
            secondary_color=rio.Color.from_hex("0083ffff"),
            mode=self.value
        )


@rio.page(
    name="Tic Tac Toe",
    url_segment=""
)
class MainPage(rio.Component):
    _diff: Diff = Diff.EASY
    _size: int = 3
    _theme: Theme = Theme.DARK
    _start: bool = False
    _board: Board | None = None
    _winner: CellState | None = None
    _thinking: bool = False

    def get_board(self: Self) -> Board:
        if self._board is None:
            self._board = Board(self._size)
        return self._board

    def reset_board(self: Self) -> None:
        self._board = None
        self._winner = None
        self._start = False

    def switch_theme(self: Self) -> None:
        self._theme = self._theme.opposite()
        self.session.theme = self._theme.get_settings()

    def make_selector(self: Self) -> rio.Component:
        return rio.Card(
            rio.Column(
                rio.Button(
                    "Switch theme",
                    icon="material/dark_mode" if self._theme == Theme.LIGHT else "material/light_mode",
                    on_press=lambda: self.switch_theme()
                ),
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
                rio.Button("Play", on_press=lambda: setattr(self, "_start", True)),
            align_x=0.5,
            align_y=0.2,
            min_width=30
        ))

    async def on_cell_press(self: Self, ref: CellRef) -> None:
        with Lock():
            if self._winner is not None:
                return
            board = self.get_board()
            board.player_move(ref)
            self._winner = board.detect_wins_or_draws()
            if self._winner is not None:
                return
            self._thinking = True
            board.cpu_move(self._diff)
            self._thinking = False
            self._winner = board.detect_wins_or_draws()

    def make_grid(self: Self) -> rio.Component:
        ref_grid = CellRef.generate_grid(self._size)
        field: list[list[rio.Component]] = []
        for row in ref_grid:
            field.append([
                comps.Cell(
                    get_board=self.get_board,
                    on_press=functools.partial(self.on_cell_press, ref),
                    ref=ref,
                    dim=False
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
            if self._winner == CellState.EMPTY:
                text = "It's a draw."
            text = "You lose."
        if self._thinking:
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
