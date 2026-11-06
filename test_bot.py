import chess

from bot import Bot
from load_bot import load_bot

print("=== BOT TEST ===\n")

bot_name = input("Bot Adı: ")

dna = load_bot(bot_name)

bot = Bot(dna)

board = chess.Board()

print("\nBaşlangıç Pozisyonu:\n")
print(board)

legal_moves = list(board.legal_moves)

move = bot.choose_move(legal_moves, board)

print("\nSeçilen Hamle:")
print(move)