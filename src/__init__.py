from .board import *
from .components import MainPage
import rio

app = rio.App(name='Tic Tac Toe', build=MainPage, theme=rio.Theme.pair_from_colors(
    primary_color=rio.Color.from_hex("01dffdff"),
    secondary_color=rio.Color.from_hex("0083ffff"),
), assets_dir=None)
