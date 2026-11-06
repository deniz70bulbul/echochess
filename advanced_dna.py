from dna_analyzer import (
    analyze_dna
)

from move_signature import (
    analyze_move_signature
)


def build_advanced_dna(
    username
):

    dna = analyze_dna(
        username
    )

    sig = analyze_move_signature(
        username
    )

    aggression = min(
        100,
        int(
            dna.get(
                "aggression",
                0
            ) * 20
            +
            sig.get(
                "checks",
                0
            ) * 0.2
        )
    )

    risk = min(
        100,
        int(
            dna.get(
                "risk",
                0
            )
        )
    )

    tactical = min(
        100,
        int(
            sig.get(
                "captures",
                0
            ) * 0.05
            +
            sig.get(
                "checks",
                0
            ) * 0.5
        )
    )

    positional = min(
        100,
        int(
            sig.get(
                "center_pawn_push",
                0
            ) * 0.3
        )
    )

    opening_loyalty = min(
        100,
        int(
            dna.get(
                "opening_loyalty",
                0
            )
        )
    )

    dev_speed = sig.get(
        "development_speed",
        0
    )

    if isinstance(
        dev_speed,
        list
    ):

        if len(dev_speed) > 0:

            dev_speed = (
                sum(dev_speed)
                /
                len(dev_speed)
            )

        else:

            dev_speed = 20

    development_style = max(
        0,
        min(
            100,
            int(
                100
                -
                dev_speed * 5
            )
        )
    )

    return {
        "aggression": aggression,
        "risk": risk,
        "tactical": tactical,
        "positional": positional,
        "opening_loyalty": opening_loyalty,
        "development_style": development_style
    }