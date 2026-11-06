import random

from opening_book_builder import (
    build_opening_book
)


def get_book_move(
    username,
    moves_played
):

    book = build_opening_book(
        username
    )

    position_key = " ".join(
        moves_played
    )

    if position_key not in book:
        return None

    candidates = book[
        position_key
    ]

    weighted_moves = []

    for move, count in candidates.items():

        for _ in range(count):
            weighted_moves.append(
                move
            )

    return random.choice(
        weighted_moves
    )