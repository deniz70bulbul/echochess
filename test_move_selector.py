import chess

from engine_wrapper import (
    get_top_moves
)

from move_selector import (
    select_move
)


board = chess.Board()

moves = get_top_moves(board)

dna = {
    "aggression": 80,
    "risk": 70
}

selected = select_move(
    moves,
    dna
)

print(
    "Selected:",
    selected
)