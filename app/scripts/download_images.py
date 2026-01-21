import requests
import pandas as pd
import os
import json
import sqlite3
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Lets get environment variables
path_images = os.getenv("PATH_IMAGES")
path_db = os.getenv("PATH_DATABASE_LOCAL")
path_keys = os.getenv("PATH_KEYS")


def download_images(df: pd.DataFrame, directory: str = path_images) -> None:
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
    data_directory: str = path_db,
) -> None:
    """
    Download images for a specific set from the SQLite database.
    Valid set_key and expansion_key pairs are:
    - main_sets_ids: OP01 to OP14-EB04 or the most recent main set
    - starter_sets_ids: ST01 to ST29 or the most recent starter set
    - extra_sets_ids: EB01 to EB02 or the most recent extra set
    - best_sets_ids: Best sets
    - other_sets_ids: Other, Promotion_Card

    Kwargs:
    dowload_directory: Directory to save images. Defaults to "app/images/{expansion_key}".
    data_directory: Directory where SQLite database is stored. Defaults to "app/db".
    """
    if dowload_directory is None:
        dowload_directory = f"{path_images}/{expansion_key}"

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

    db_path = os.path.join(data_directory, "card_sets.db")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cur = conn.cursor()

        # Fetch all cards for the specific expansion
        cur.execute(
            f"SELECT UID, UIL FROM {table_name} WHERE expansion_key = ?",
            (expansion_key,),
        )
        rows = cur.fetchall()

        if not rows:
            print(f"No cards found for {expansion_key} in {table_name}")
            conn.close()
            return

        os.makedirs(dowload_directory, exist_ok=True)
        printed_half = False

        for index, row in enumerate(rows):
            img_url = row["UIL"]
            card_id = row["UID"]
            file_path = os.path.join(dowload_directory, f"{card_id}.png")

            try:
                response = requests.get(img_url, stream=True)
                response.raise_for_status()
                with open(file_path, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
                if not printed_half and index >= len(rows) // 2:
                    print("50% downloaded")
                    printed_half = True
            except requests.exceptions.RequestException as e:
                print(f"Could not download {card_id}.png from {img_url}: {e}")

        conn.close()
        print("All images downloaded.")
    except Exception as e:
        print(f"Error downloading images from SQLite: {e}")


def dowload_all_set_imgs(
    dowload_directory: str = "app/images",
    data_directory: str = path_db,
    keys_directory: str = path_keys,
) -> None:
    """
    Download images for all sets from the SQLite database.
    Kwargs:
    dowload_directory: Base directory to save images. Defaults to "app/images".
    data_directory: Directory where SQLite database is stored. Defaults to "app/db".
    keys_directory: Path to the JSON file containing set IDs. Defaults to "app/sets_ids.json".
    """
    with open(keys_directory, "r", encoding="utf-8") as f:
        data = json.load(f)

    for set_key, expansions in data.items():
        for expansion_key in expansions.keys():
            print(f"Downloading images for {set_key} - {expansion_key}")
            dowload_set_imgs(
                set_key=set_key,
                expansion_key=expansion_key,
                dowload_directory=f"{dowload_directory}/{expansion_key}",
                data_directory=data_directory,
            )
    print("All sets downloaded.")
