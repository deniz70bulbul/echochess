import os

def delete_bot(bot_name):

    filename = f"bots/{bot_name}.json"

    if os.path.exists(filename):
        os.remove(filename)
        print(f"{bot_name} silindi.")
    else:
        print("Bot bulunamadı.")