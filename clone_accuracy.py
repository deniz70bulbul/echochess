from style_analyzer import (
    analyze_style
)

from dna_analyzer import (
    analyze_dna
)

from profile_analyzer import (
    get_opening_percentages
)


def calculate_clone_accuracy(
    username
):

    style = analyze_style(
        username
    )

    dna = analyze_dna(
        username
    )

    openings = (
        get_opening_percentages(
            username
        )
    )

    score = 0

    if len(openings) >= 3:
        score += 35

    if style.get(
        "castling_rate",
        0
    ) > 70:
        score += 10

    if style.get(
        "average_game_length",
        0
    ) > 20:
        score += 10

    if style.get(
        "opening_diversity",
        0
    ) > 20:
        score += 15

    if dna.get(
        "risk",
        0
    ) > 10:
        score += 15

    if dna.get(
        "aggression",
        0
    ) > 1:
        score += 15

    return min(
        score,
        100
    )