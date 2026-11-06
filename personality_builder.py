from advanced_dna import (
    build_advanced_dna
)

from opening_loyalty import (
    build_opening_loyalty
)

from gambit_preference import (
    analyze_gambit_preference
)


def build_personality(
    username
):

    dna = build_advanced_dna(
        username
    )

    loyalty = build_opening_loyalty(
        username
    )

    gambit = (
        analyze_gambit_preference(
            username
        )
    )

    labels = []

    if dna["aggression"] >= 70:
        labels.append(
            "Aggressive"
        )

    if dna["tactical"] >= 60:
        labels.append(
            "Tactical"
        )

    if dna["positional"] >= 60:
        labels.append(
            "Positional"
        )

    if loyalty[
        "loyalty_score"
    ] >= 40:
        labels.append(
            "Opening Loyalist"
        )

    if gambit[
        "gambit_rate"
    ] >= 25:
        labels.append(
            "Gambit Lover"
        )

    if not labels:

        labels.append(
            "Balanced Player"
        )

    return {
        "personality":
            labels,

        "aggression":
            dna["aggression"],

        "risk":
            dna["risk"],

        "tactical":
            dna["tactical"],

        "positional":
            dna["positional"]
    }