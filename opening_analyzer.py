import chess
import chess.pgn
import json
import os


def load_eco_database():

    eco_database = {}

    eco_files = [
        "ecoA.json",
        "ecoB.json",
        "ecoC.json",
        "ecoD.json",
        "ecoE.json"
    ]

    for file_name in eco_files:

        path = os.path.join(
            "data",
            file_name
        )

        if not os.path.exists(path):
            continue

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            eco_database.update(data)

    return eco_database


def detect_opening(pgn_file):

    eco_database = load_eco_database()

    with open(
        pgn_file,
        "r",
        encoding="utf-8"
    ) as pgn:

        game = chess.pgn.read_game(pgn)

    if game is None:
        return "Unknown"

    board = game.board()

    last_opening = "Unknown"

    for move in game.mainline_moves():

        board.push(move)

        fen = board.fen()

        fen_key = fen
        
        

        if fen_key in eco_database:

            opening_data = eco_database[fen_key]

            if "name" in opening_data:
                last_opening = opening_data["name"]

    return last_opening