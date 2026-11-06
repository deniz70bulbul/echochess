import chess

from engine_wrapper import (
    get_top_moves
)

board = chess.Board()

moves = get_top_moves(board)

for move in moves:

    print(move)