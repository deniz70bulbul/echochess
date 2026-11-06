import chess

from move_classifier import (
    classify_move
)

board = chess.Board()

move = chess.Move.from_uci(
    "e2e4"
)

print(
    classify_move(
        board,
        move
    )
)