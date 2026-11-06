import os
import chess
import chess.pgn


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100
}


def is_sacrifice_like(board, move):
    piece = board.piece_at(move.from_square)

    if piece is None:
        return False

    piece_value = PIECE_VALUES.get(piece.piece_type, 0)

    if piece_value < 2:
        return False

    if piece.piece_type == chess.KING:
        return False

    board_after = board.copy(stack=False)
    board_after.push(move)

    target_square = move.to_square

    opponent = not piece.color

    opponent_attackers = len(
        board_after.attackers(opponent, target_square)
    )

    own_defenders = len(
        board_after.attackers(piece.color, target_square)
    )

    if opponent_attackers == 0:
        return False

    if opponent_attackers > own_defenders:
        return True

    return False


def analyze_sacrifices(username):
    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    result = {
        "games": 0,
        "sacrifice_moves": 0,
        "total_moves": 0,
        "sacrifice_rate": 0,
        "sacrifice_style": "low"
    }

    if not os.path.exists(pgn_folder):
        return result

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
        ) as pgn_file:

            game = chess.pgn.read_game(pgn_file)

        if game is None:
            continue

        result["games"] += 1

        board = game.board()

        for move in game.mainline_moves():

            result["total_moves"] += 1

            if is_sacrifice_like(board, move):
                result["sacrifice_moves"] += 1

            board.push(move)

    if result["total_moves"] > 0:
        result["sacrifice_rate"] = round(
            result["sacrifice_moves"] / result["total_moves"] * 100,
            1
        )

    if result["sacrifice_rate"] >= 10:
        result["sacrifice_style"] = "high"
    elif result["sacrifice_rate"] >= 4:
        result["sacrifice_style"] = "moderate"
    else:
        result["sacrifice_style"] = "low"

    return result