from typing import Self, Callable
from ..board import Board
from ..cells import CellRef, CellState
import rio


_SIZE = 4


class Cell(rio.Component):
    get_board: Callable[[], Board]
    on_press: rio.EventHandler[[]]
    ref: CellRef
    dim: bool

    def build(self: Self) -> rio.Component:
        value = self.ref.get(self.get_board().get())

        if value == CellState.EMPTY:
            return rio.Card(
                content=rio.Spacer(
                    min_width=_SIZE,
                    min_height=_SIZE
                ),
                on_press=self.on_press
            )

        color = rio.Color.RED if value == CellState.X else rio.Color.BLUE

        if self.dim:
            color = color.replace(opacity=0.2)

        return rio.Icon(
            "material/close" if value == CellState.X else "material/circle",
            fill=color,
            min_width=_SIZE,
            min_height=_SIZE
        )

