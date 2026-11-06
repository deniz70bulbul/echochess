import os


def get_pgn_count(username):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    if not os.path.exists(pgn_folder):
        return 0

    return len([
        file
        for file in os.listdir(pgn_folder)
        if file.endswith(".pgn")
    ])


def can_create_bot(username):

    pgn_count = get_pgn_count(
        username
    )

    return pgn_count >= 10