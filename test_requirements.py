from bot_requirements import (
    get_pgn_count,
    can_create_bot
)

username = "KULLANICI_ADIN"

print(
    "PGN Count:",
    get_pgn_count(username)
)

print(
    "Can Create Bot:",
    can_create_bot(username)
)