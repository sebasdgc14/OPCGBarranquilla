from bs4 import BeautifulSoup
import requests
import pandas as pd
import os


def scrape_set(url: str) -> pd.DataFrame:
    """
    Scrape card data from the given URL and return it as a DataFrame.
    """
    cardlist_db = requests.get(url).text  # Set Card List Page
    soup = BeautifulSoup(cardlist_db, "lxml")
    main = soup.find("main", class_="mainCol")
    card_info = main.find_all("dl", class_="modalCol")  # All info for card
    set_lenght = len(card_info)
    set_db = pd.DataFrame()

    for index in range(set_lenght):
        # All card information
        unique_id = card_info[index].get("id")
        unique_img_link = f"https://en.onepiece-cardgame.com/images/cardlist/card/{unique_id}.png?251031"
        info = card_info[index].find("div", class_="getInfo")
        if info:  # This is exclusively to handle ST14 brook in ST26 which has not set info listed
            print_set = info.h3.next_sibling.text
        else:
            print_set = ""
        # Public info
        id = card_info[index].span.text
        rarity = card_info[index].find_all("span")[1].text
        name = card_info[index].find("div", class_="cardName").text
        card_type = (
            card_info[index].find("div", class_="feature").h3.next_sibling.split("/")
        )
        color = card_info[index].find("div", class_="color").h3.next_sibling.split("/")
        effect = card_info[index].find("div", class_="text").contents[1::2]
        block = card_info[index].find("div", class_="block").h3.next_sibling
        attribute = card_info[index].find("div", class_="attribute").i.text
        power = card_info[index].find("div", class_="power").h3.next_sibling.text
        cost = card_info[index].find("div", class_="cost").h3.next_sibling.text
        counter = card_info[index].find("div", class_="counter").h3.next_sibling.text
        # Structure
        card = {
            "UID": unique_id,
            "UIL": unique_img_link,
            "Set": print_set,
            "ID": id,
            "name": name,
            "rarity": rarity,
            "type": card_type,
            "color": color,
            "attribute": attribute,
            "block": block,
            "power": power,
            "cost": cost,
            "counter": counter,
            "effect": effect,
        }
        set_db = pd.concat([set_db, pd.DataFrame([card])], ignore_index=True)
    return set_db


def download_images(df: pd.DataFrame, directory: str) -> None:
    """
    Download images from URLs in the DataFrame and save them to the specified folder.
    """
    os.makedirs(directory, exist_ok=True)
    for index, row in df.iterrows():
        img_url = row["UIL"]
        card_id = row["UID"]
        file_path = os.path.join(directory, f"{card_id}.png")
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)
            print(f"Downloaded {card_id}.png")
        except requests.exceptions.RequestException as e:
            print(f"Could not download {card_id}.png from {img_url}: {e}")


card_set_url = "https://en.onepiece-cardgame.com/cardlist/?series=569026"
set_dataframe = scrape_set(card_set_url)
print(set_dataframe)
# download_images(set_dataframe, "images")
