from style_analyzer import analyze_style


def analyze_dna(username):

    style = analyze_style(username)

    aggression = (
        style["gambit_rate"] * 0.4
        +
        style["early_queen_rate"] * 0.3
        +
        (100 - style["average_game_length"]) * 0.3
    )

    risk = (
        style["gambit_rate"] * 0.5
        +
        style["opening_diversity"] * 0.3
        +
        style["early_queen_rate"] * 0.2
    )

    opening_loyalty = (
        100 - style["opening_diversity"]
    )

    aggression = max(
        0,
        min(
            100,
            round(aggression, 1)
        )
    )

    risk = max(
        0,
        min(
            100,
            round(risk, 1)
        )
    )

    opening_loyalty = max(
        0,
        min(
            100,
            round(opening_loyalty, 1)
        )
    )

    return {
        "aggression": aggression,
        "risk": risk,
        "opening_loyalty": opening_loyalty
    }