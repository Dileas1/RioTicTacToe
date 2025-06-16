import sys
from src import *


def main():
    board = Board(3)
    players_turn = True
    print(board)
    while (not board.is_full()) and (board.check_for_win() == CellState.EMPTY):
        if players_turn:
            print(f"\n\x1b[1F", end='')
            move = list(map(int, input().split()))
            print(f"\x1b[1F", end='')
            if not board.player_move(CellRef(move[0], move[1])):
                continue
        else:
            board.medium_diff_move()
        players_turn = not players_turn
        print(f"\x1b[{board.size() * 2 - 1}F", end='')
        print(board)
        print('\x1b[0K', end='')
    winner = board.check_for_win()
    print(f"Winner: {winner}" if winner != CellState.EMPTY else "Draw.")


if __name__ == "__main__":
    main()
    sys.exit(0)
