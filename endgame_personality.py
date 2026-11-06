import os
import chess
import chess.pgn


def count_material(board):

    count = 0

    for piece in board.piece_map().values():

        if piece.piece_type != chess.KING:

            count += 1

    return count


def analyze_endgame_personality(
    username
):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    result = {
        "games": 0,
        "simplification": 0,
        "fighting": 0,
        "endgame_style": "unknown"
    }

    if not os.path.exists(
        pgn_folder
    ):
        return result

    simplification_score = 0
    fighting_score = 0

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
        ) as pgn_file:

            game = chess.pgn.read_game(
                pgn_file
            )

        if game is None:
            continue

        result["games"] += 1

        board = game.board()

        materials = []

        for move in game.mainline_moves():

            board.push(
                move
            )

            materials.append(
                count_material(
                    board
                )
            )

        if len(materials) < 10:
            continue

        last_part = materials[
            int(
                len(materials)
                * 0.7
            ):
        ]

        if len(last_part) < 2:
            continue

        start_material = (
            last_part[0]
        )

        end_material = (
            last_part[-1]
        )

        material_drop = (
            start_material
            -
            end_material
        )

        if material_drop >= 4:

            simplification_score += 1

        else:

            fighting_score += 1

    total = (
        simplification_score
        +
        fighting_score
    )

    if total > 0:

        result[
            "simplification"
        ] = round(
            simplification_score
            /
            total
            *
            100,
            1
        )

        result[
            "fighting"
        ] = round(
            fighting_score
            /
            total
            *
            100,
            1
        )

    if (
        simplification_score
        >
        fighting_score
    ):

        result[
            "endgame_style"
        ] = "simplifier"

    else:

        result[
            "endgame_style"
        ] = "fighter"

    return result