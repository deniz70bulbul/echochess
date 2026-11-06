import os
import chess
import chess.engine


ENGINE_PATH = os.environ.get(
    "STOCKFISH_PATH",
    "stockfish-windows-x86-64-avx2.exe" if os.name == "nt" else "bin/stockfish",
)


def get_engine():

    return chess.engine.SimpleEngine.popen_uci(
        ENGINE_PATH
    )


def get_best_move(
    board,
    think_time=0.2
):

    engine = get_engine()

    result = engine.play(
        board,
        chess.engine.Limit(
            time=think_time
        )
    )

    engine.quit()

    return result.move


def get_top_moves(
    board,
    count=5,
    think_time=0.3
):

    engine = get_engine()

    analysis = engine.analyse(
        board,
        chess.engine.Limit(
            time=think_time
        ),
        multipv=count
    )

    engine.quit()

    moves = []

    for line in analysis:

        move = line["pv"][0]

        score = line["score"]

        moves.append({
            "move": move,
            "score": str(score)
        })

    return moves