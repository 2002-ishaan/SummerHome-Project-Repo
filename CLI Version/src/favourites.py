import os
import json


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Create the data folder if it doesn't exist


LISTINGS_FILE = os.path.join(
    DATA_DIR, "cleaned_listings.csv"
)  # CSV of cleaned listings
FAV_FILE = os.path.join(DATA_DIR, "favorites.json")  # JSON file storing user favorites


def load_favorites():
    """
    Load all favorites from favorites.json.

    - If the file doesn't exist yet, return an empty dict.
    - If the file exists but is corrupted, also return an empty dict.
    - This ensures we always have a safe, usable structure for favorite listings.
    """
    if not os.path.exists(FAV_FILE):
        return {}
    try:
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_favorites(favs: dict):
    """
    Save the entire favorites dictionary back to favorites.json.

    - Overwrites the old file with the latest user favorites.
    - Uses indent=4 for readability in case we want to inspect manually.
    """
    with open(FAV_FILE, "w") as f:
        json.dump(favs, f, indent=4)


def get_user_favorites(user_id: str):
    """
    Retrieve the favorite listings for a specific user.

    - Loads all favorites from the file.
    - Returns a list of listing IDs for this user.
    - Returns an empty list if the user has no favorites yet.
    """
    favs = load_favorites()
    return favs.get(user_id, [])


def add_favorite(user_id: str, listing_id: int):
    """
    Add a listing to a user's favorites.

    - Loads the current favorites from the file.
    - Checks if the listing is already in the user's favorites to avoid duplicates.
    - Appends the listing ID if not already present.
    - Saves the updated favorites back to the JSON file.
    - Returns True to indicate success.
    """
    favs = load_favorites()
    user_list = favs.get(user_id, [])
    if listing_id not in user_list:
        user_list.append(listing_id)
    favs[user_id] = user_list
    save_favorites(favs)
    return True


def remove_favorite(user_id: str, listing_id: int):
    """
    Remove a listing from a user's favorites.

    - Loads current favorites from the file.
    - Checks if the listing exists in the user's favorites.
    - Removes it if present and saves the updated favorites.
    - Returns True if removal was successful, False if the listing was not found.
    """
    favs = load_favorites()
    user_list = favs.get(user_id, [])
    if listing_id in user_list:
        user_list.remove(listing_id)
        favs[user_id] = user_list
        save_favorites(favs)
        return True
    return False
