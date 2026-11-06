import json

def load_bot(bot_name):

    filename = f"bots/{bot_name}.json"

    with open(filename, "r", encoding="utf-8") as file:
        dna = json.load(file)

    return dna