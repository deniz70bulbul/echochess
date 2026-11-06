import os

from opening_analyzer import detect_opening


def analyze_user(username):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    openings = {}

    if not os.path.exists(pgn_folder):
        return openings

    for file in os.listdir(pgn_folder):

        if not file.endswith(".pgn"):
            continue

        path = os.path.join(
            pgn_folder,
            file
        )

        opening = detect_opening(path)

        if opening not in openings:
            openings[opening] = 0

        openings[opening] += 1

    return openings


def get_opening_percentages(username):

    openings = analyze_user(username)

    total_games = sum(
        openings.values()
    )

    if total_games == 0:
        return {}

    result = {}

    for opening, count in openings.items():

        result[opening] = {
            "count": count,
            "percent": round(
                count /
                total_games *
                100,
                1
            )
        }

    return result