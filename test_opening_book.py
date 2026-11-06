from opening_book_builder import (
    build_opening_book
)

book = build_opening_book(
    "mudur"
)

for position, moves in book.items():

    print(
        position,
        "->",
        moves
    )