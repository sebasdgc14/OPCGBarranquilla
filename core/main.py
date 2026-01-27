from scripts import download_images as download

# from scripts import upload_to_neon as up_neon
from db.database import SessionLocal
from scripts import scrape_build_database as scrape


def run_scrape():
    db = SessionLocal()
    URL = "https://en.onepiece-cardgame.com/cardlist/?series=569028"
    try:
        scrape.scrape_set(URL, "starter", db)
        print("Database updated successfully.")
    finally:
        db.close()


def run_scrape_all():
    db = SessionLocal()
    try:
        scrape.scrape_all_sets(db)
        print("All database updated successfully.")
    finally:
        db.close()


def main() -> None:
    print("Running everything")
    # scrape.scrape_all_sets()
    # run_scrape()
    # scrape.scrape_and_append_set("starter_sets_ids", "ST29")
    # df = scrape.scrape_set("https://en.onepiece-cardgame.com/cardlist/?series=569029")
    # download.dowload_set_imgs("-GREEN/YELLOW Yamato- [ST-28]")
    # up_neon.upload_tables_to_neon()


# to run use uv run -m core.main
if __name__ == "__main__":
    main()
