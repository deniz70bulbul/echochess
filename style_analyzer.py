import os
import chess.pgn

from profile_analyzer import analyze_user


def analyze_style(username):

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    result = {
        "opening_diversity": 0,
        "gambit_rate": 0,
        "average_game_length": 0,
        "castling_rate": 0,
        "early_queen_rate": 0
    }

    if not os.path.exists(pgn_folder):
        return result

    total_games = 0
    total_moves = 0
    castled_games = 0
    early_queen_games = 0

    openings = analyze_user(username)

    gambit_games = 0

    for opening_name in openings:

        if "gambit" in opening_name.lower():
            gambit_games += openings[opening_name]

    for file in os.listdir(pgn_folder):

        if not file.endswith(".pgn"):
            continue

        total_games += 1

        path = os.path.join(
            pgn_folder,
            file
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as pgn:

            game = chess.pgn.read_game(pgn)

        if game is None:
            continue

        board = game.board()

        move_count = 0

        castled = False

        queen_moved_early = False

        for move in game.mainline_moves():

            piece = board.piece_at(
                move.from_square
            )

            move_count += 1

            if piece:

                if (
                    piece.symbol().lower() == "k"
                    and abs(
                        chess.square_file(
                            move.to_square
                        )
                        -
                        chess.square_file(
                            move.from_square
                        )
                    ) > 1
                ):
                    castled = True

                if (
                    piece.symbol().lower() == "q"
                    and move_count <= 10
                ):
                    queen_moved_early = True

            board.push(move)

        total_moves += move_count

        if castled:
            castled_games += 1

        if queen_moved_early:
            early_queen_games += 1

    if total_games == 0:
        return result

    result["opening_diversity"] = round(
        len(openings)
        /
        total_games
        * 100,
        1
    )

    result["gambit_rate"] = round(
        gambit_games
        /
        total_games
        * 100,
        1
    )

    result["average_game_length"] = round(
        total_moves
        /
        total_games,
        1
    )

    result["castling_rate"] = round(
        castled_games
        /
        total_games
        * 100,
        1
    )

    result["early_queen_rate"] = round(
        early_queen_games
        /
        total_games
        * 100,
        1
    )

    return result