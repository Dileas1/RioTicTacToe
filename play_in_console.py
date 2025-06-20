from src import *

board = Board(5)
players_turn = True
print(board)
winner = board.detect_wins_or_draws()
while winner is None:
    if players_turn:
        print(f"\n\x1b[1F", end='')
        move = list(map(int, input().split()))
        print(f"\x1b[1F", end='')
        if not board.player_move(CellRef(move[0], move[1])):
            continue
    else:
        board.cpu_move(Diff.MED)
    players_turn = not players_turn
    print(f"\x1b[{board.size() * 2 - 1}F", end='')
    print(board)
    print('\x1b[0K', end='')
    winner = board.detect_wins_or_draws()
print(f"Winner: {winner}" if winner != CellState.EMPTY else "Draw.")
