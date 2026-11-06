import os

def list_bots():

    if not os.path.exists("bots"):
        return []

    bots = []

    for file in os.listdir("bots"):

        if file.endswith(".json"):
            bots.append(file[:-5])

    return bots