import os
import chess.pgn


def build_opening_book(
    username,
    max_ply=12
):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    book = {}

    if not os.path.exists(pgn_folder):
        return book

    for file in os.listdir(pgn_folder):

        if not file.endswith(".pgn"):
            continue

        path = os.path.join(
            pgn_folder,
            file
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as pgn:

            game = chess.pgn.read_game(
                pgn
            )

        if game is None:
            continue

        moves = []

        for move in game.mainline_moves():

            moves.append(
                move.uci()
            )

            if len(moves) >= max_ply:
                break

        for i in range(
            len(moves)
        ):

            position_key = " ".join(
                moves[:i]
            )

            next_move = moves[i]

            if position_key not in book:
                book[position_key] = {}

            if (
                next_move
                not in
                book[position_key]
            ):
                book[position_key][
                    next_move
                ] = 0

            book[position_key][
                next_move
            ] += 1

    return book