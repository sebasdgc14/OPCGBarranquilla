from bs4 import BeautifulSoup
import requests

index = 9

op01_cardlist_db = requests.get(
    "https://en.onepiece-cardgame.com/cardlist/?series=569101"
).text  # OP-01 Card List Page
op01_soup = BeautifulSoup(op01_cardlist_db, "lxml")
op01_main = op01_soup.find("main", class_="mainCol")
card_info = op01_main.find_all(
    "dl", class_="modalCol"
)  # Contains all information about each card in the set
# print(card_info[index])

## All card information
unique_id = card_info[index].get("id")
unique_img_link = (
    f"https://en.onepiece-cardgame.com/images/cardlist/card/{unique_id}.png?251031"
)
print_set = card_info[index].find("div", class_="getInfo").h3.next_sibling.text
# Public info
id = card_info[index].span.text
rarity = card_info[index].find_all("span")[1].text
name = card_info[index].find("div", class_="cardName").text
card_type = card_info[index].find("div", class_="feature").h3.next_sibling.split("/")
color = card_info[index].find("div", class_="color").h3.next_sibling.split("/")
effect = card_info[index].find("div", class_="text").contents[1::2]
block = card_info[index].find("div", class_="block").h3.next_sibling
attribute = card_info[index].find("div", class_="attribute").i.text
power = card_info[index].find("div", class_="power").h3.next_sibling.text
cost = card_info[index].find("div", class_="cost").h3.next_sibling.text
counter = card_info[index].find("div", class_="counter").h3.next_sibling.text

print(f"Unique id: {unique_id}")
print(f"Unique img link: {unique_img_link}")
print(print_set)
print("----------------")
print(f"Card id: {id}")
print(f"Card rarity: {rarity}")
print(f"Card name: {name}")
print(f"Card types: {card_type}")
print(f"Card colors: {color}")
print(f"Card effect: {effect}")
print(f"Card block: {block}")
print(f"Card attribute: {attribute}")
print(f"Card power: {power}")
print(f"Card cost: {cost}")
print(f"Card counter: {counter}")
