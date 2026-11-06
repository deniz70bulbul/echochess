import chess

from move_history import (
    get_moves_played
)

board = chess.Board()

board.push_uci(
    "e2e4"
)

board.push_uci(
    "c7c6"
)

board.push_uci(
    "d2d4"
)

print(
    get_moves_played(
        board
    )
)