import os
import requests
import logging
from lor_deckcodes import LoRDeck
import json

def setup_logger(log_filename):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def download_cards_json(download_folder):
    # Check if cards.json exists in the download folder
    json_file_path = os.path.join(download_folder, "cards.json")
    if os.path.exists(json_file_path):
        return

    # If the file does not exist, download it
    download_url = "https://hextechoracle.com/lor/content/data/cards.json"
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(json_file_path, "wb") as json_file:
            json_file.write(response.content)
        logging.info("Downloaded cards.json")
    else:
        logging.error("Failed to download cards.json")

def decode_deck(deck_code, cards_data):
    try:
        # Decode the deck code using LoRDeck.from_deckcode
        deck = LoRDeck.from_deckcode(deck_code)

        # Create a list to store card information
        cards_list = []

        # Collect card information (card_code, count, name, cost, rarity, type) for each card in the deck
        for card in deck.cards:
            card_count = card.count
            card_code = card.card_code

            # Get card information from cards_data using card_code
            if card_code in cards_data:
                card_info = cards_data[card_code]
                card_name = card_info["name"]
                card_cost = card_info["cost"]
                card_rarity = card_info["rarity"]
                card_type = card_info["type"]

                # Check rarity and type conditions
                cards_list.append((card_cost, card_name, card_count, card_rarity, card_type))
            else:
                logging.warning(f"Card with code {card_code} not found in cards.json")

        # Sort the cards_list first by card cost, then by card name
        cards_list.sort(key=lambda x: (x[0], x[1]))

        return cards_list

    except ValueError:
        logging.error("Invalid deck code")
        return []

def print_deck_contents(deck_code, cards_list):
    logging.info(f"Deck Code: {deck_code}")
    separator = "-" * 60

    # Print cards inside cards_list whose rarity is "Champion"
    logging.info("Champion Cards:")
    for card in cards_list:
        if card[3] == "Champion":
            pretty_format = f"Cost: {card[0]:>2}, Name: {card[1]:<30}, Count: {card[2]:>2}"
            logging.info(pretty_format)

    # Print cards inside cards_list whose type is "Unit" and rarity is not "Champion"
    logging.info("Unit Cards (Non-Champion):")
    for card in cards_list:
        if card[3] != "Champion" and card[4] == "Unit":
            pretty_format = f"Cost: {card[0]:>2}, Name: {card[1]:<30}, Count: {card[2]:>2}"
            logging.info(pretty_format)

    # Print cards inside cards_list whose type is "Spell"
    logging.info("Spell Cards:")
    for card in cards_list:
        if card[4] == "Spell":
            pretty_format = f"Cost: {card[0]:>2}, Name: {card[1]:<30}, Count: {card[2]:>2}"
            logging.info(pretty_format)

    # Print a separator 60 characters long
    logging.info(separator)

def load_cards_data(download_folder):
    json_file_path = os.path.join(download_folder, "cards.json")
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

def main():
    # Define the download folder
    download_folder = "/workspaces/chatGPT-experiments/deckCompare/download"

    # Set up logging
    log_filename = "log.txt"
    setup_logger(log_filename)

    # Download cards.json if needed
    download_cards_json(download_folder)

    # Load cards.json into a variable
    cards_data = load_cards_data(download_folder)

    # Deck codes to decode
    deck_code1 = "CEBAIAIFB4WDANQIAEAQGDAUDAQSIJZUAIAQCBIFAEAQCBAA"
    deck_code2 = "CEBAGAIFB4WDACABAEBQYFAYEESCONACAEAQCBACAECQKNQBAEAQKHI"

    # Call the function to decode and print the decks
    result1 = decode_deck(deck_code1, cards_data)
    result2 = decode_deck(deck_code2, cards_data)

    # Print the deck contents with pretty formatting and separator
    print_deck_contents(deck_code1, result1)
    print_deck_contents(deck_code2, result2)

    # Diff the second result versus the first one
    diff_results(result1, result2)

def diff_results(result1, result2):
    # Find cards missing in result2 compared to result1
    missing_in_result2 = [card for card in result1 if card not in result2]

    # Find cards missing in result1 compared to result2
    missing_in_result1 = [card for card in result2 if card not in result1]

    logging.info("Difference between Result 1 and Result 2:")

    if missing_in_result1:
        logging.info("Cards missing in Result 1:")
        for card in missing_in_result1:
            pretty_format = f"Cost: {card[0]:>2}, Name: {card[1]:<30}, Count: {card[2]:>2}"
            logging.info(pretty_format)

    if missing_in_result2:
        logging.info("Cards missing in Result 2:")
        for card in missing_in_result2:
            pretty_format = f"Cost: {card[0]:>2}, Name: {card[1]:<30}, Count: {card[2]:>2}"
            logging.info(pretty_format)

if __name__ == "__main__":
    main()
