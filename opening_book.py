import json

def save_opening_book(bot_name, moves):

    filename = f"bots/{bot_name}_opening.json"

    data = {
        "opening_book": moves
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"\nOpening Book kaydedildi: {filename}")