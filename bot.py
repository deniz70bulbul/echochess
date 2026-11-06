import random
import chess

class Bot:

    def __init__(self, dna):
        self.dna = dna

    def score_move(self, move, board):

        score = 0

        # TAŞ ALMA
        if board.is_capture(move):
            score += self.dna["aggressive"] * 0.2

        # GELİŞİM
        piece = board.piece_at(move.from_square)

        if piece:

            if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:

                if board.fullmove_number <= 10:
                    score += self.dna["development"] * 0.15

        # TAŞ DEĞİŞİMİ
        if board.is_capture(move):

            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)

            if attacker and victim:

                if attacker.piece_type == victim.piece_type:
                    score += self.dna["exchange"] * 0.15

        # RİSK
        if random.randint(0, 1000) < self.dna["risk"]:
            score += random.randint(0, 50)

        return score

    def choose_move(self, moves, board):

        best_move = None
        best_score = -999999

        for move in moves:

            score = self.score_move(move, board)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move