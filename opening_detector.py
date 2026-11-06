import json
import chess.pgn


def detect_opening(pgn_file):

    with open(
        "data/openings.json",
        "r",
        encoding="utf-8"
    ) as f:

        openings = json.load(f)

    with open(
        pgn_file,
        encoding="utf-8"
    ) as f:

        game = chess.pgn.read_game(f)

    if game is None:
        return "Unknown"

    moves = []

    board = game.board()

    for move in game.mainline_moves():

        moves.append(move.uci())

        board.push(move)

        sequence = " ".join(moves)

        if sequence in openings:
            return openings[sequence]

    return "Unknown"