import os

from opening_analyzer import (
    detect_opening
)


GAMBIT_KEYWORDS = [

    "Gambit",

    "Benko",

    "Budapest",

    "Evans",

    "Smith-Morra",

    "Blackmar",

    "Wing Gambit",

    "Danish",

    "King's Gambit",

    "Queen's Gambit"
]


def analyze_gambit_preference(
    username
):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    total_games = 0

    gambit_games = 0

    if not os.path.exists(
        pgn_folder
    ):
        return {
            "gambit_games": 0,
            "total_games": 0,
            "gambit_rate": 0
        }

    for file in os.listdir(
        pgn_folder
    ):

        if not file.endswith(
            ".pgn"
        ):
            continue

        total_games += 1

        path = os.path.join(
            pgn_folder,
            file
        )

        opening = detect_opening(
            path
        )

        for keyword in GAMBIT_KEYWORDS:

            if keyword.lower() in opening.lower():

                gambit_games += 1

                break

    rate = 0

    if total_games > 0:

        rate = round(
            gambit_games
            /
            total_games
            *
            100,
            1
        )

    return {
        "gambit_games":
            gambit_games,

        "total_games":
            total_games,

        "gambit_rate":
            rate
    }