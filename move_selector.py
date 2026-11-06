import random


def select_move(
    moves,
    dna
):

    aggression = dna.get(
        "aggression",
        50
    )

    risk = dna.get(
        "risk",
        50
    )

    if len(moves) == 1:
        return moves[0]

    if aggression >= 70:

        top_range = min(
            3,
            len(moves)
        )

        return random.choice(
            moves[:top_range]
        )

    if aggression >= 40:

        top_range = min(
            2,
            len(moves)
        )

        return random.choice(
            moves[:top_range]
        )

    return moves[0]