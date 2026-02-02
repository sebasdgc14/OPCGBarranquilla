import requests
import pandas as pd
import os
import json
import sqlite3
from typing import Optional
from core.config import settings

path_images = settings.PATH_IMAGES
path_db = settings.PATH_DATABASE_LOCAL
path_keys = settings.PATH_KEYS


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


def _safe_dir_name(value: str) -> str:
    return value.replace("/", "-").replace("\\", "-")


def dowload_set_imgs(
    print_set: str,
    dowload_directory: Optional[str] = None,
    data_directory: str = path_db,
) -> None:
    """
    Download images for a specific set from the SQLite database using print_set.

    Kwargs:
    dowload_directory: Directory to save images. Defaults to "images/{print_set}".
    data_directory: Directory where SQLite database is stored. Defaults to "db".
    """
    if dowload_directory is None:
        safe_print_set = _safe_dir_name(print_set)
        dowload_directory = f"{path_images}/{safe_print_set}"

    db_path = os.path.join(data_directory, "cards.db")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cur = conn.cursor()

        cur.execute(
            "SELECT unique_id, unique_img_link FROM Cards WHERE print_set = ?",
            (print_set,),
        )
        rows = cur.fetchall()

        if not rows:
            print(f"No cards found for print_set {print_set}")
            conn.close()
            return

        os.makedirs(dowload_directory, exist_ok=True)
        printed_half = False

        for index, row in enumerate(rows):
            img_url = row["unique_img_link"]
            card_id = row["unique_id"]
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
    dowload_directory: str = "images",
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
