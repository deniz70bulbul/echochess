import chess

from clone_engine_v2 import (
    get_clone_move
)

board = chess.Board()

result = get_clone_move(
    "deniz",
    board
)

print(result)