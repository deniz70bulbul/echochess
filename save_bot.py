import json

def save_bot(bot_name, dna):

    filename = f"bots/{bot_name}.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dna, file, indent=4)

    print(f"\nBot kaydedildi: {filename}")