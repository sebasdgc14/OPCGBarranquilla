from fastapi import FastAPI, HTTPException
# import CardTypes

app = FastAPI()

listings = [{"id": 1, "title": "Listing One"}, {"id": 2, "title": "Listing Two"}]


@app.get("/home")
def home():
    """
    A simple home endpoint to verify the API is running.
    """
    return {"message": "Welcome to the One Piece Card Game API!"}


@app.get("/database")
def database():
    """
    An endpoint to return the entire card database.
    """
    return {"cards": []}  # Placeholder for actual card data


@app.get("/my_listings")
def my_listings():
    """
    An endpoint to return a list of all listings for sale by the user.
    """
    return {"listings": listings}


@app.get("/my_listings/{listing_id}")
def get_listing(listing_id: int):
    """
    An endpoint to return details of a specific listing by its ID.
    """
    listing = listings[listing_id - 1]
    if listing_id not in range(1, len(listings) + 1):
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
