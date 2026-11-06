import os
import chess.pgn


def analyze_move_signature(username):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    stats = {
        "games": 0,

        "early_castle": 0,
        "early_queen": 0,

        "knight_before_bishop": 0,

        "center_pawn_push": 0,
        "edge_pawn_push": 0,

        "king_side_castle": 0,
        "queen_side_castle": 0,

        "captures": 0,
        "checks": 0,

        "development_speed": []
    }

    if not os.path.exists(
        pgn_folder
    ):
        return stats

    for file in os.listdir(
        pgn_folder
    ):

        if not file.endswith(
            ".pgn"
        ):
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

        stats["games"] += 1

        board = game.board()

        move_number = 0

        knight_moves = 0
        bishop_moves = 0

        developed = set()

        for move in game.mainline_moves():

            move_number += 1

            piece = board.piece_at(
                move.from_square
            )

            uci = move.uci()

            if board.is_capture(
                move
            ):
                stats[
                    "captures"
                ] += 1

            if board.gives_check(
                move
            ):
                stats[
                    "checks"
                ] += 1

            if uci in [
                "e2e4",
                "d2d4",
                "e7e5",
                "d7d5"
            ]:
                stats[
                    "center_pawn_push"
                ] += 1

            if uci in [
                "a2a4",
                "a7a5",
                "h2h4",
                "h7h5"
            ]:
                stats[
                    "edge_pawn_push"
                ] += 1

            if uci in [
                "e1g1",
                "e8g8"
            ]:

                stats[
                    "king_side_castle"
                ] += 1

                if move_number <= 10:

                    stats[
                        "early_castle"
                    ] += 1

            if uci in [
                "e1c1",
                "e8c8"
            ]:

                stats[
                    "queen_side_castle"
                ] += 1

                if move_number <= 10:

                    stats[
                        "early_castle"
                    ] += 1

            if piece:

                symbol = (
                    piece.symbol()
                    .lower()
                )

                if (
                    symbol == "q"
                    and move_number <= 10
                ):
                    stats[
                        "early_queen"
                    ] += 1

                if symbol == "n":

                    knight_moves += 1

                if symbol == "b":

                    bishop_moves += 1

                if (
                    symbol in [
                        "n",
                        "b"
                    ]
                    and
                    move.from_square
                    not in developed
                ):

                    developed.add(
                        move.from_square
                    )

            board.push(
                move
            )

        if knight_moves > bishop_moves:

            stats[
                "knight_before_bishop"
            ] += 1

        if len(
            developed
        ) >= 4:

            stats[
                "development_speed"
            ].append(
                move_number
            )

    if len(
        stats[
            "development_speed"
        ]
    ) > 0:

        stats[
            "development_speed"
        ] = round(
            sum(
                stats[
                    "development_speed"
                ]
            )
            /
            len(
                stats[
                    "development_speed"
                ]
            ),
            1
        )

    else:

        stats[
            "development_speed"
        ] = 0

    return stats