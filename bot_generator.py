from dna_analyzer import analyze_dna
from opening_dna import get_opening_dna
from bot_requirements import can_create_bot


def generate_bot_profile(username):

    if not can_create_bot(username):

        return {
            "success": False,
            "message": "Minimum 10 PGN required"
        }

    dna = analyze_dna(username)

    openings = get_opening_dna(username)

    return {
        "success": True,
        "username": username,
        "dna": dna,
        "openings": openings
    }