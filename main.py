from dna import create_dna
from save_bot import save_bot
from load_bot import load_bot
from list_bots import list_bots
from delete_bot import delete_bot

print("=== CHESS BOT V1 ===\n")

print("1 - Yeni Bot Oluştur")
print("2 - Kayıtlı Bot Aç")
print("3 - Bot Sil")

choice = input("\nSeçim: ")

if choice == "1":

    bot_name = input("\nBot Adı: ")

    dna = create_dna()

    save_bot(bot_name, dna)

elif choice == "2":

    bots = list_bots()

    print("\nKAYITLI BOTLAR\n")

    for i, bot in enumerate(bots, start=1):
        print(f"{i}. {bot}")

    bot_name = input("\nAçılacak bot adı: ")

    dna = load_bot(bot_name)

    print("\nBOT DNA'SI\n")

    for key, value in dna.items():
        print(key, ":", value)

elif choice == "3":

    bots = list_bots()

    print("\nKAYITLI BOTLAR\n")

    for i, bot in enumerate(bots, start=1):
        print(f"{i}. {bot}")

    bot_name = input("\nSilinecek bot adı: ")

    delete_bot(bot_name)

else:

    print("Geçersiz seçim.")