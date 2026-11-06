import chess.pgn
import json
import os


def detect_opening(pgn_file):

    with open(pgn_file, encoding="utf-8") as pgn:
        game = chess.pgn.read_game(pgn)

    if game is None:
        return "Unknown"

    moves = []

    for move in game.mainline_moves():

        moves.append(move.uci())

        if len(moves) >= 12:
            break

    sequence = " ".join(moves)

    database_file = os.path.join(
        "data",
        "openings.json"
    )

    if not os.path.exists(database_file):
        return "Unknown"

    with open(
        database_file,
        "r",
        encoding="utf-8"
    ) as f:

        openings = json.load(f)

    best_match = "Unknown"
    longest_match = 0

    for opening_moves, opening_name in openings.items():

        if sequence.startswith(opening_moves):

            move_count = len(
                opening_moves.split()
            )

            if move_count > longest_match:

                longest_match = move_count
                best_match = opening_name

    return best_match