from move_classifier import (
    classify_move
)


def score_move_style(
    board,
    move,
    profile
):

    score = 0

    tags = classify_move(
        board,
        move
    )

    dna = profile[
        "advanced_dna"
    ]

    signature = profile[
        "move_signature"
    ]

    if (
        "capture" in tags
        and
        dna["aggression"] > 60
    ):

        score += 20

    if (
        "check" in tags
        and
        dna["aggression"] > 60
    ):

        score += 25

    if (
        "center_control" in tags
        and
        dna["positional"] > 50
    ):

        score += 15

    if (
        "development" in tags
        and
        signature.get(
            "development_speed",
            0
        )
    ):

        score += 10

    if (
        "queen_move" in tags
        and
        signature.get(
            "early_queen",
            0
        ) < 5
    ):

        score -= 20

    return score