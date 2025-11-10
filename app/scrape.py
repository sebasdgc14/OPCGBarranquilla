from bs4 import BeautifulSoup
import requests

op01_cardlist_db = requests.get(
    "https://en.onepiece-cardgame.com/cardlist/?series=569101"
).text  # OP-01 Card List Page
op01_soup = BeautifulSoup(op01_cardlist_db, "lxml")
op01_main = op01_soup.find("main", class_="mainCol")
card_info = op01_main.find_all(
    "dl", class_="modalCol"
)  # Contains all information about each card in the set
print(f"cardinfo: {card_info[7]}")

id = card_info[7].span.text
b = card_info[7].find("dl")

print(f"Card id: {id}")
print(f"b: {b}")
