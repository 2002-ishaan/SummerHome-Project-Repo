import pandas as pd
import os


Listings_File = os.path.join(
    os.path.dirname(__file__),  # Current file directory (src/)
    "..",  # Go up one level (to LLM_SummerHome_Recommender/)
    "data",  # Go into data folder
    "cleaned_listings.csv",  # Your dataset
)


# for _, row in df.iterrows() means:
# "Go through my DataFrame one row at a time"
# "Give me each row's data (ignore the row number)"
# "Let me work with each row individually"
# .iterrows() = A method that iterates through each row of the DataFrame


"""
Listing Class
-------------
Represents a single listing/property in our system.
We give each listing a unique ID to make it easy to reference,
especially when managing favorites, bookings, or recommendations.
"""


class Listing:
    def __init__(
        self,
        name,
        location,
        property_type,
        accommodates,
        amenities,
        price,
        min_nights,
        max_nights,
        review_rating,
        tags,
        listing_id: int,
    ):
        self.listing_id = listing_id  # Unique identifier for each listing
        self.name = name
        self.location = location
        self.property_type = property_type
        self.accommodates = accommodates
        self.amenities = amenities
        self.price = price
        self.min_nights = min_nights
        self.max_nights = max_nights
        self.review_rating = review_rating
        self.tags = tags

    def to_dict(self):
        # Converting Listing object to Dictionary to save as JSON
        return {
            "listing_id": self.listing_id,  # <--- Listing ID added here
            "name": self.name,
            "location": self.location,
            "property_type": self.property_type,
            "accommodates": self.accommodates,
            "amenities": self.amenities,
            "price": self.price,
            "min_nights": self.min_nights,
            "max_nights": self.max_nights,
            "review_rating": self.review_rating,
            "tags": self.tags,
        }


# This function loads your CSV data using pandas.read_csv.
# Checks if file exists; if not, prints error and returns empty list.
# Then uses a list comprehension with df.iterrows() to iterate row by row.
# For each row, it creates a Listing object with the data from that row.
# Finally returns a list of Listing objects.


def load_listings(filename=Listings_File):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []
    df = pd.read_csv(filename)
    listings = [
        Listing(
            name=row["name"],
            location=row["location"],
            property_type=row["property_type"],
            accommodates=row["accommodates"],
            amenities=row["amenities"],
            price=row["price"],
            min_nights=row["min_nights"],
            max_nights=row["max_nights"],
            review_rating=row["review_rating"],
            tags=row["tags"],
            listing_id=i,  # <--- NEW (stable, 0..N-1)
        )
        for i, (_, row) in enumerate(df.iterrows())
    ]
    print(f"Loaded {len(listings)} listings from {filename}.")
    return listings


def view_listings(listings, limit=5):
    """
    Print a list of listings to the CLI in a human-readable format.

    - Shows the first `limit` listings.
    - Displays all key info: name, location, type, accommodates, price, rating, tags.
    """

    if not listings:
        print("No listings available.")
        return

    print(
        f"\n ------ Showing {min(limit, len(listings))} of {len(listings)} listings ------"
    )
    for listing in listings[:limit]:
        print(f"[ID: {listing.listing_id}] {listing.name}")  # <--- show Listing ID
        print(f"Name: {listing.name}")
        print(f"Location: {listing.location}")
        print(f"Type: {listing.property_type} | Accommodates: {listing.accommodates}")
        print(f"Price: ${listing.price} | Rating: {listing.review_rating}")
        print(f"Tags: {listing.tags}")
        print("-" * 40)


# Filter Functions


def find_listing_by_id(listings, listing_id: int):
    """Return the listing object with the given ID, or None if not found."""
    for l in listings:
        if l.listing_id == listing_id:
            return l
    return None


def filter_by_environment(listings, environment):
    """
    Filter listings by environment keyword.

    - Checks if the environment keyword is in either tags or location (case-insensitive).
    """

    environment = environment.lower()
    return [
        listing
        for listing in listings
        if environment in str(listing.tags).lower()
        or environment in str(listing.location).lower()
    ]


def filter_by_budget(listings, min_price, max_price):
    """Return listings whose price falls within min_price and max_price."""
    return [listing for listing in listings if min_price <= listing.price <= max_price]


def search_by_location(listings, location_preference):
    """Filter listings by location keyword (case-insensitive)."""
    location_preference = location_preference.lower()
    return [
        listing
        for listing in listings
        if location_preference in listing.location.lower()
    ]


def search_by_property_type(listings, property_type_perference):

    property_type_perference = property_type_perference.lower()
    return [
        listing
        for listing in listings
        if property_type_perference in listing.property_type.lower()
    ]


# This function sorts listings with attribute chosen by user.
# It uses a built-in sorted() with a key function to get the attribute from each listing.
# The reverse=not ascending means descending if ascending=False.

# def sort_listings(listings, by_what="price", ascending=True):

#     valid_sort_keys = ["price", "review_rating", "accommodates"]
#     if by_what not in valid_sort_keys:
#         print(f"Invalid sort key. Choose from: {', '.join(valid_sort_keys)}")
#         return listings

#     def get_key(listing):
#         return getattr(listing, by_what)

#     sorted_list = sorted(listings, key=get_key, reverse=not ascending)
#     return sorted_list


def sort_listings(listings, by_what="price", ascending=True, user=None):

    valid_sort_keys = ["price", "review_rating", "accommodates"]
    if by_what not in valid_sort_keys:
        print(f"Invalid sort key. Choose from: {', '.join(valid_sort_keys)}")
        return listings

    filtered_listings = listings
    if user:
        filtered_listings = [
            l
            for l in listings
            if user.budget_min <= l.price <= user.budget_max
            and l.accommodates >= user.group_size
        ]

    sorted_list = sorted(
        filtered_listings, key=lambda l: getattr(l, by_what), reverse=not ascending
    )
    return sorted_list


def get_listing_details(listings, index):

    if 0 <= index < len(listings):
        listing = listings[index]
        print("\n--- Listing Details ---")
        for key, value in listing.to_dict().items():
            print(f"{key.capitalize()}: {value}")
        print("-" * 40)
        return listing
    else:
        print("Invalid index.")
        return None


def filter_combined(
    listings, environment=None, min_price=None, max_price=None, min_accommodates=None
):
    """
    Apply multiple filters in one go.

    - environment: filter by keyword in tags or location
    - min_price, max_price: filter by budget
    - min_accommodates: filter by minimum number of guests
    - Returns a filtered list of listings
    """
    filtered = listings

    if environment:
        filtered = filter_by_environment(filtered, environment)
    if min_price is not None and max_price is not None:
        filtered = filter_by_budget(filtered, min_price, max_price)
    if min_accommodates is not None:
        filtered = filter_by_accommodates(filtered, min_accommodates)

    return filtered


def filter_by_accommodates(listings, min_accommodates):

    return [listing for listing in listings if listing.accommodates >= min_accommodates]


if __name__ == "__main__":

    def get_input_limit(default=5):
        limit = input(
            f"How many listings should I show you? (default {default}): "
        ).strip()
        return int(limit) if limit.isdigit() else default

    def view_listings_cli(listings):
        limit = get_input_limit(default=5)
        view_listings(listings, limit=limit)

    def filter_listings_cli(listings):
        env = input(
            "Filter by environment (e.g., beach, city) or leave blank: "
        ).strip()
        min_price = input("Minimum price or leave blank: ").strip()
        max_price = input("Maximum price or leave blank: ").strip()

        filtered = listings
        if env:
            filtered = filter_by_environment(filtered, env)
        if (
            min_price
            and max_price
            and min_price.replace(".", "", 1).isdigit()
            and max_price.replace(".", "", 1).isdigit()
        ):
            filtered = filter_by_budget(filtered, float(min_price), float(max_price))
        elif min_price or max_price:
            print("Both min and max price required to filter by budget.")

        if filtered:
            limit = get_input_limit(default=len(filtered))
            view_listings(filtered, limit=limit)
        else:
            print("No listings match your criteria.")

    def filter_by_accommodates_cli(listings):

        min_acc = input("Enter minimum number of guests to accommodate: ").strip()
        if not min_acc.isdigit():
            print("Please enter a valid integer number.")
            return
        min_acc = int(min_acc)

        filtered = filter_by_accommodates(listings, min_acc)

        if not filtered:
            print(f"No listings found that accommodate at least {min_acc} guests.")
            return

        limit = get_input_limit(default=len(filtered))
        view_listings(filtered, limit=limit)

    def sort_listings_cli(listings):
        print("Sort by: price, review_rating, accommodates")
        sort_key = input("Enter sort field: ").strip()
        order = input("Ascending? (yes/no): ").strip().lower()
        ascending = True if order in ["yes", "y", ""] else False

        sorted_list = sort_listings(listings, by=sort_key, ascending=ascending)

        limit = get_input_limit(default=10)
        view_listings(sorted_list, limit=limit)

    def combined_filters_cli(listings):
        env = input(
            "Filter by environment (e.g., beach, city) or leave blank if you don't wanna filter: "
        ).strip()
        min_price = input(
            "Minimum price or leave blank if you don't wanna filter: "
        ).strip()
        max_price = input(
            "Maximum price or leave blank if you don't wanna filter: "
        ).strip()
        min_acc = input(
            "Minimum accommodates or leave blank if you don't wanna filter: "
        ).strip()

        # Convert to correct types or None
        min_price = (
            float(min_price) if min_price.replace(".", "", 1).isdigit() else None
        )
        max_price = (
            float(max_price) if max_price.replace(".", "", 1).isdigit() else None
        )
        min_acc = int(min_acc) if min_acc.isdigit() else None

        filtered = filter_combined(
            listings,
            environment=env if env else None,
            min_price=min_price,
            max_price=max_price,
            min_accommodates=min_acc,
        )

        if filtered:
            limit = get_input_limit(default=len(filtered))
            view_listings(filtered, limit=limit)
        else:
            print("No listings match your criteria.")

    def listings_menu():
        listings = load_listings()
        while True:
            print("\n=== Listings Menu ===")
            print("1. View listings")
            print("2. Filter listings by environment and budget")
            print("3. Sort listings")
            print("4. Filter by accommodates")
            print("5. Combined filters (environment + budget + accommodates)")
            print("6. Exit to main menu")

            choice = input("Choose an option: ").strip()
            if choice == "1":
                view_listings_cli(listings)
            elif choice == "2":
                filter_listings_cli(listings)
            elif choice == "3":
                sort_listings_cli(listings)
            elif choice == "4":
                filter_by_accommodates_cli(listings)
            elif choice == "5":
                combined_filters_cli(listings)
            elif choice == "6":
                print("Returning to main menu...")
                break
            else:
                print("Invalid choice, try again.")

    listings_menu()
