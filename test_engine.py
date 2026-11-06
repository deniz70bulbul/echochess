import chess

from engine_wrapper import (
    get_best_move
)

board = chess.Board()

move = get_best_move(board)

print(move)