from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import json
from typing import Optional


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
        card_type = ",".join(
            card_info[index].find("div", class_="feature").h3.next_sibling.split("/")
        )
        color = ",".join(
            card_info[index].find("div", class_="color").h3.next_sibling.split("/")
        )
        effect = ",".join(
            [str(e) for e in card_info[index].find("div", class_="text").contents[1::2]]
        )
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


def scrape_all_sets(
    download_directory: str = "app/info", keys_directory: str = "app/sets_ids.json"
) -> None:
    """
    Scrape all sets defined in the JSON file and return a concatenated DataFrame.
    Kwargs:
    download_directory: Directory to save the scraped data. Defaults to "app/info".
    keys_directory: Path to the JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    with open("app/sets_ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    main_sets_df = {}
    starter_sets_df = {}
    extra_sets_df = {}
    best_sets_df = {}
    other_sets_df = {}
    os.makedirs(download_directory, exist_ok=True)
    for set_key, expansions in data.items():
        for expansion_key in expansions.keys():
            set_id = data.get(set_key).get(expansion_key)
            print(f"Scraping info for {set_key} - {expansion_key}")
            df = scrape_set(
                f"https://en.onepiece-cardgame.com/cardlist/?series=569{set_id}"
            )
            if set_key == "main_sets_ids":
                main_sets_df[f"{expansion_key}"] = df
            elif set_key == "starter_sets_ids":
                starter_sets_df[f"{expansion_key}"] = df
            elif set_key == "extra_sets_ids":
                extra_sets_df[f"{expansion_key}"] = df
            elif set_key == "best_sets_ids":
                best_sets_df[f"{expansion_key}"] = df
            elif set_key == "other_sets_ids":
                other_sets_df[f"{expansion_key}"] = df

    set_names = [
        "main_sets_df",
        "starter_sets_df",
        "extra_sets_df",
        "best_sets_df",
        "other_sets_df",
    ]
    for i, a in enumerate(
        [main_sets_df, starter_sets_df, extra_sets_df, best_sets_df, other_sets_df]
    ):
        with pd.HDFStore(
            os.path.join(download_directory, f"{set_names[i]}_sets.h5"), mode="w"
        ) as store:
            for key, df in a.items():
                store.put(key, df, format="table", data_columns=True)
    return None


def download_images(df: pd.DataFrame, directory: str) -> None:
    """
    Download images from URLs in the DataFrame and save them to the specified folder.
    """
    os.makedirs(directory, exist_ok=True)
    printed_half = False
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
            if not printed_half and index >= df.shape[0] // 2:
                print("50% downloaded")
                printed_half = True
        except requests.exceptions.RequestException as e:
            print(f"Could not download {card_id}.png from {img_url}: {e}")
    print("All images downloaded.")


def dowload_set_imgs(
    set_key: str,
    expansion_key: str,
    dowload_directory: Optional[str] = None,
    keys_directory: str = "app/sets_ids.json",
) -> None:
    """
    Download images for a specific set key from the JSON file.
    Valid set_key and expansion_key pairs are:
    - main_sets_ids: OP-01 to OP-13 or the most recent main set
    - starter_sets_ids: ST-01 to ST-28 or the most recent starter set
    - extra_sets_ids: EB-01 to EB-02 or the most recent extra set
    - other_sets_ids: Other, Promotion_Card

    Kwargs:
    keys_directory: Path to the JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    if dowload_directory is None:
        dowload_directory = f"app/images/{expansion_key}"
    with open(keys_directory, "r", encoding="utf-8") as f:
        data = json.load(f)
    set_id = data.get(set_key).get(expansion_key)
    if not set_id or set_id is None:
        print(
            f"Set key '{set_key}' not found in expansion '{expansion_key}'. \n Make sure to check the expansion_key spelling."
        )
        return
    card_set_url = f"https://en.onepiece-cardgame.com/cardlist/?series=569{set_id}"
    set_dataframe = scrape_set(card_set_url)
    download_images(set_dataframe, dowload_directory)


def dowload_all_set_imgs(
    dowload_directory: str = "app/images", keys_directory: str = "app/sets_ids.json"
) -> None:
    """
    Download images for all sets defined in the JSON file.
    Kwargs:
    dowload_directory: Base directory to save images. Defaults to "app/images".
    keys_directory: Path to the JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    with open("app/sets_ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for set_key, expansions in data.items():
        for expansion_key in expansions.keys():
            print(f"Downloading images for {set_key} - {expansion_key}")
            dowload_set_imgs(
                set_key=set_key,
                expansion_key=expansion_key,
                dowload_directory=f"app/images/{expansion_key}",
                keys_directory="app/sets_ids.json",
            )
    print("All sets downloaded.")


if __name__ == "__main__":
    print("Running scrape_and_build.py")
    scrape_all_sets()
    # df = scrape_set("https://en.onepiece-cardgame.com/cardlist/?series=569801")
    # download_images(df, "app/images/Others")
    # dowload_set_imgs("main_sets_ids", "OP-01")
    # dowload_all_set_imgs()
