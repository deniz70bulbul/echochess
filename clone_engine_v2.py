import random

from bot_profile_loader import (
    load_bot_profile
)

from engine_wrapper import (
    get_top_moves
)

from move_selector import (
    select_move
)

from move_history import (
    get_moves_played
)


def get_clone_move(
    username,
    board
):

    profile = load_bot_profile(
        username
    )

    if profile is None:

        return None

    moves_played = get_moves_played(
        board
    )

    position_key = " ".join(
        moves_played
    )

    opening_book = profile[
        "opening_book"
    ]

    if position_key in opening_book:

        candidates = opening_book[
            position_key
        ]

        weighted_moves = []

        for move, count in candidates.items():

            for _ in range(count):

                weighted_moves.append(
                    move
                )

        return {
            "source": "opening_book",
            "move": random.choice(
                weighted_moves
            )
        }

    top_moves = get_top_moves(
        board
    )

    selected = select_move(
        top_moves,
        profile["dna"]
    )

    return {
        "source": "dna_engine",
        "move": str(
            selected["move"]
        )
    }