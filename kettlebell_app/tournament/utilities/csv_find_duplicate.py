import csv
from collections import defaultdict


def process_csv(input_file, output_file):
    players = defaultdict(set)

    with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    for row in data:
        player_key = (row["Imię"], row["Nazwisko"], row["Klub"])
        category = row["Kategoria"]
        players[player_key].add(category)

    new_data = []
    for row in data:
        player_key = (row["Imię"], row["Nazwisko"], row["Klub"])
        if players[player_key]:
            row["Kategoria"] = ", ".join(players[player_key])
            players[player_key].clear()
            new_data.append(row)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_data)


input_file = "../../lista/all_players.csv"
output_file = "../../lista/all_players_without_duplicate.csv"
process_csv(input_file, output_file)
print("Przetwarzanie zakończone. Wyniki zapisano w", output_file)
