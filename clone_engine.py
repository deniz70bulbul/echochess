import chess

from opening_player import (
    get_book_move
)

from engine_wrapper import (
    get_top_moves
)

from move_selector import (
    select_move
)

from dna_analyzer import (
    analyze_dna
)


def get_clone_move(
    username,
    board,
    moves_played
):

    book_move = get_book_move(
        username,
        moves_played
    )

    if book_move is not None:

        return {
            "source": "opening_book",
            "move": book_move
        }

    dna = analyze_dna(
        username
    )

    moves = get_top_moves(
        board
    )

    selected = select_move(
        moves,
        dna
    )

    return {
        "source": "dna_engine",
        "move": str(
            selected["move"]
        )
    }