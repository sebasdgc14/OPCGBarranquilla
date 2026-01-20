from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import json
import sqlite3
from dotenv import load_dotenv

load_dotenv()  # Lets get environment variables
path_images = os.getenv("PATH_IMAGES")
path_db = os.getenv("PATH_DATABASE_LOCAL")
path_keys = os.getenv("PATH_KEYS")


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
    download_directory: str = path_db, keys_directory: str = path_keys
) -> None:
    """
    Scrape all sets defined in the JSON file and store them in a SQLite database.
    Kwargs:
    download_directory: Directory to save the SQLite database. Defaults to "app/db".
    keys_directory: Path to the JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    with open(keys_directory, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(download_directory, exist_ok=True)
    db_path = os.path.join(download_directory, "card_sets.db")

    # Create database and establish connection
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables for each set category
    set_categories = {
        "main_sets_ids": "main_sets",
        "starter_sets_ids": "starter_sets",
        "extra_sets_ids": "extra_sets",
        "best_sets_ids": "best_sets",
        "other_sets_ids": "other_sets",
    }

    for table_name in set_categories.values():
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expansion_key TEXT NOT NULL,
                UID TEXT UNIQUE NOT NULL,
                UIL TEXT,
                "Set" TEXT,
                card_id TEXT,
                name TEXT,
                rarity TEXT,
                type TEXT,
                color TEXT,
                attribute TEXT,
                block TEXT,
                power TEXT,
                cost TEXT,
                counter TEXT,
                effect TEXT
            )
        """)

    conn.commit()

    # Scrape and insert data
    for set_key, expansions in data.items():
        table_name = set_categories.get(set_key)
        if not table_name:
            print(f"Unknown set_key: {set_key}")
            continue

        for expansion_key in expansions.keys():
            set_id = data.get(set_key).get(expansion_key)
            print(f"Scraping info for {set_key} - {expansion_key}")

            df = scrape_set(
                f"https://en.onepiece-cardgame.com/cardlist/?series=569{set_id}"
            )

            # Insert DataFrame rows into SQLite
            for _, row in df.iterrows():
                try:
                    cur.execute(
                        f"""
                        INSERT INTO {table_name} 
                        (expansion_key, UID, UIL, "Set", card_id, name, rarity, type, color, 
                         attribute, block, power, cost, counter, effect)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            expansion_key,
                            row["UID"],
                            row["UIL"],
                            row["Set"],
                            row["ID"],
                            row["name"],
                            row["rarity"],
                            row["type"],
                            row["color"],
                            row["attribute"],
                            row["block"],
                            row["power"],
                            row["cost"],
                            row["counter"],
                            row["effect"],
                        ),
                    )
                except sqlite3.IntegrityError:
                    print(f"  Skipping duplicate card: {row['UID']}")

            conn.commit()

    conn.close()
    print(f"Database saved to: {db_path}")
    return None


def scrape_and_append_set(
    set_key: str,
    expansion_key: str,
    data_directory: str = path_db,
    keys_directory: str = path_keys,
) -> None:
    """
    Scrape a single new set and append it to the corresponding SQLite table.

    Args:
        set_key: The category key (e.g., "main_sets_ids", "starter_sets_ids", "extra_sets_ids", "best_sets_ids", "other_sets_ids")
        expansion_key: The specific expansion (e.g., "OP01", "ST01", "EB01")
        data_directory: Directory where SQLite database is stored. Defaults to "app/db".
        keys_directory: Path to JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    with open(keys_directory, "r", encoding="utf-8") as f:
        data = json.load(f)

    set_id = data.get(set_key, {}).get(expansion_key)
    if not set_id:
        print(
            f"Set key '{set_key}' with expansion '{expansion_key}' not found in {keys_directory}.\n"
            f"Make sure the set_key and expansion_key are spelled correctly."
        )
        return

    # Map set_key to table name
    set_table_map = {
        "main_sets_ids": "main_sets",
        "starter_sets_ids": "starter_sets",
        "extra_sets_ids": "extra_sets",
        "best_sets_ids": "best_sets",
        "other_sets_ids": "other_sets",
    }

    table_name = set_table_map.get(set_key)
    if not table_name:
        print(f"Unknown set_key: {set_key}")
        return

    # Scrape the set
    print(f"Scraping {set_key} - {expansion_key}")
    df = scrape_set(f"https://en.onepiece-cardgame.com/cardlist/?series=569{set_id}")

    # Append to the SQLite database
    db_path = os.path.join(data_directory, "card_sets.db")

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        for _, row in df.iterrows():
            try:
                cur.execute(
                    f"""
                    INSERT INTO {table_name} 
                    (expansion_key, UID, UIL, "Set", card_id, name, rarity, type, color, 
                     attribute, block, power, cost, counter, effect)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        expansion_key,
                        row["UID"],
                        row["UIL"],
                        row["Set"],
                        row["ID"],
                        row["name"],
                        row["rarity"],
                        row["type"],
                        row["color"],
                        row["attribute"],
                        row["block"],
                        row["power"],
                        row["cost"],
                        row["counter"],
                        row["effect"],
                    ),
                )
            except sqlite3.IntegrityError:
                print(f"  Skipping duplicate card: {row['UID']}")

        conn.commit()
        conn.close()
        print(f"Successfully appended {expansion_key} to {table_name}")
    except Exception as e:
        print(f"Error appending to SQLite database: {e}")


# if __name__ == "__main__":
#     print("Running scrape_and_build.py")
#     scrape_and_append_set("starter_sets_ids", "ST29")
#     scrape_all_sets()
#     df = scrape_set("https://en.onepiece-cardgame.com/cardlist/?series=569029")
#     download_images(df)
#     dowload_set_imgs("starter_sets_ids", "ST29")
#     dowload_all_set_imgs()
