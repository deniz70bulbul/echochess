import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci(
    "stockfish-windows-x86-64-avx2.exe"
)

board = chess.Board()

result = engine.play(
    board,
    chess.engine.Limit(time=0.1)
)

print(
    "Best Move:",
    result.move
)

engine.quit()