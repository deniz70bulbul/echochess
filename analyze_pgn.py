import chess.pgn

from opening_book import save_opening_book

BOT_NAME = "DenizBot"

pgn_file = open(
    "lichess_pgn_2026.06.02_L04d1ng_vs_chessfan3142.bc280uQw.pgn",
    encoding="utf-8"
)

game = chess.pgn.read_game(pgn_file)

board = game.board()

moves = []

move_count = 0

for move in game.mainline_moves():

    san_move = board.san(move)

    moves.append(san_move)

    board.push(move)

    move_count += 1

    if move_count >= 20:
        break

save_opening_book(BOT_NAME, moves)

print("\nOPENING BOOK\n")

for move in moves:
    print(move)