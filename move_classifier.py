import chess


def classify_move(
    board,
    move
):

    tags = []

    piece = board.piece_at(
        move.from_square
    )

    if piece is None:
        return tags

    symbol = (
        piece.symbol()
        .lower()
    )

    if board.is_capture(
        move
    ):
        tags.append(
            "capture"
        )

    if board.gives_check(
        move
    ):
        tags.append(
            "check"
        )

    to_square = (
        chess.square_name(
            move.to_square
        )
    )

    if to_square in [
        "d4",
        "d5",
        "e4",
        "e5"
    ]:

        tags.append(
            "center_control"
        )

    if symbol in [
        "n",
        "b"
    ]:

        tags.append(
            "development"
        )

    if symbol == "q":

        tags.append(
            "queen_move"
        )

    if symbol == "p":

        tags.append(
            "pawn_move"
        )

    return tags