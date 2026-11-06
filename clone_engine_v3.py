import random

from bot_profile_loader import (
    load_bot_profile
)

from engine_wrapper import (
    get_top_moves
)

from move_history import (
    get_moves_played
)

from move_scorer import (
    score_move_style
)


def score_move(
    move_data,
    profile
):

    score = 0

    dna = profile[
        "advanced_dna"
    ]

    if dna[
        "aggression"
    ] > 60:

        score += random.randint(
            5,
            15
        )

    if dna[
        "tactical"
    ] > 60:

        score += random.randint(
            5,
            15
        )

    if profile[
        "opening_loyalty"
    ][
        "loyalty_score"
    ] > 40:

        score += random.randint(
            5,
            10
        )

    if profile[
        "gambit_preference"
    ][
        "gambit_rate"
    ] > 25:

        score += random.randint(
            5,
            10
        )

    return score


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

        for move, count in (
            candidates.items()
        ):

            for _ in range(
                count
            ):

                weighted_moves.append(
                    move
                )

        return {
            "source":
                "opening_book",

            "move":
                random.choice(
                    weighted_moves
                )
        }

    top_moves = get_top_moves(
        board,
        count=5
    )

    best_move = None

    best_score = -999999

    for move_data in top_moves:

        current_score = score_move(
            move_data,
            profile
        )

        current_score += score_move_style(
            board,
            move_data["move"],
            profile
        )

        if current_score > best_score:

            best_score = (
                current_score
            )

            best_move = (
                move_data
            )

    return {
        "source":
            "clone_v3",

        "move":
            str(
                best_move[
                    "move"
                ]
            )
    }