def get_moves_played(
    board
):

    moves = []

    for move in board.move_stack:

        moves.append(
            move.uci()
        )

    return moves