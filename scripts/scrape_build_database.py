from bs4 import BeautifulSoup
import requests
import json
from pathlib import Path
import models
from db.database import engine
from sqlalchemy.orm import Session
from db.database import SessionLocal
from core.config import settings


path_images = settings.PATH_IMAGES
path_db = settings.PATH_DATABASE_LOCAL
path_images = settings.PATH_KEYS


def scrape_set(url: str, set_type: str, db: Session):
    """
    Scrape card data from the given URL and add it to the database
    url:
    set_type: "main", "starter", "extra", "best", "other"
    db:
    """
    models.Base.metadata.create_all(bind=engine)  # Create tables

    cardlist_db = requests.get(url).text  # Set Card List Page
    soup = BeautifulSoup(cardlist_db, "lxml")
    main = soup.find("main", class_="mainCol")
    card_info = main.find_all("dl", class_="modalCol")  # All info for card

    for card in card_info:
        # All card information
        unique_id = card.get("id")
        unique_img_link = f"https://en.onepiece-cardgame.com/images/cardlist/card/{unique_id}.png?251031"
        info = card.find("div", class_="getInfo")
        print_set = (
            info.h3.next_sibling.text if info else ""
        )  # This is exclusively to handle ST14 brook in ST26 which has not set info listed
        # Public info
        id = card.span.text
        rarity = card.find_all("span")[1].text
        name = card.find("div", class_="cardName").text
        card_type = ",".join(
            card.find("div", class_="feature").h3.next_sibling.split("/")
        )
        color = ",".join(card.find("div", class_="color").h3.next_sibling.split("/"))
        block = card.find("div", class_="block").h3.next_sibling
        attribute = card.find("div", class_="attribute").i.text
        power = card.find("div", class_="power").h3.next_sibling.text
        cost = card.find("div", class_="cost").h3.next_sibling.text
        counter = card.find("div", class_="counter").h3.next_sibling.text
        effect = ",".join(
            [str(e) for e in card.find("div", class_="text").contents[1::2]]
        )
        # ORM object
        card_db = models.Cards(
            unique_id=unique_id,
            set_type=set_type,
            unique_img_link=unique_img_link,
            print_set=print_set,
            card_id=id,
            rarity=rarity,
            name=name,
            card_type=card_type,
            color=color,
            block=block,
            attribute=attribute,
            power=power,
            cost=cost,
            counter=counter,
            effect=effect,
        )
        db.add(card_db)
    db.commit()


def scrape_all_sets():
    BASE_DIR = Path(__file__).resolve().parent
    SETS_PATH = BASE_DIR / "sets_ids.json"

    with open(SETS_PATH, "r", encoding="utf-8") as f:
        SETS = json.load(f)
    for json_key, sets_dict in SETS.items():
        set_type = json_key.replace("_sets_ids", "")
        for set_code, set_id in sets_dict.items():
            url = f"https://en.onepiece-cardgame.com/cardlist/?series=569{set_id}"
            print(f"Scraping {set_code} as {set_type}")

            db = SessionLocal()
            try:
                scrape_set(url, set_type, db)
            except Exception as e:
                db.rollback()
                print(f"FAILED {set_code}: {e}")
            finally:
                db.close()
