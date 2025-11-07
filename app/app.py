from fastapi import FastAPI, HTTPException
# import CardTypes

app = FastAPI()

listings = [{"id": 1, "title": "Listing One"}, {"id": 2, "title": "Listing Two"}]


@app.get("/MyListings")
def my_listings():
    """
    An endpoint to return a list of all listings for sale by the user.
    """
    return {"listings": listings}


@app.get("/MyListings/{listing_id}")
def get_listing(listing_id: int):
    """
    An endpoint to return details of a specific listing by its ID.
    """
    listing = listings[listing_id - 1]
    if listing_id not in range(1, len(listings) + 1):
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
