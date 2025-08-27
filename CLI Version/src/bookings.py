import json
import os
from pathlib import Path
from datetime import datetime

# Path to the bookings.json file where all booking data is stored
# This keeps our data persistent between program runs

BOOKINGS_FILE = os.path.join(
    os.path.dirname(__file__),  # Current file location (inside src/)
    "..",  # Go one directory up
    "data",  # Target the data/ folder
    "bookings.json",  # Store all bookings here
)


def load_bookings():
    """
    Load all existing bookings from bookings.json.

    - If the file does not exist, it means no bookings have been made yet → return an empty list.
    - If the file exists but is corrupted (invalid JSON), we also return an empty list
      instead of crashing the program.

    This ensures the system is fault-tolerant and always returns a safe, usable list.
    """
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_bookings(bookings):
    """
    Save the updated bookings list back into bookings.json.

    - This function overwrites the old file with the new list.
    - Data is indented for readability, making it easier to debug or inspect manually.
    """
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=4)


def create_booking(user_id, listing_id, check_in=None, check_out=None):
    """
    Create a new booking and add it to the bookings.json file.

    Steps:
    1. Load all existing bookings.
    2. Generate a unique booking_id (simply 1 + number of current bookings).
    3. Store all booking details (who booked, which listing, and date range).
    4. Append this new booking to the list.
    5. Save everything back to bookings.json.
    6. Return the newly created booking (so it can be confirmed/shown to the user).
    """

    bookings = load_bookings()
    booking_id = len(bookings) + 1  # Simple way to generate unique booking IDs

    booking = {
        "booking_id": booking_id,
        "user_id": user_id,
        "listing_id": listing_id,
        "check_in": check_in,
        "check_out": check_out,
    }

    bookings.append(booking)
    save_bookings(bookings)
    return booking


def get_user_bookings(user_id):
    """
    Retrieve all bookings made by a specific user.

    - Loads all bookings from the system.
    - Filters them to only include those where user_id matches.
    - Returns a list (can be empty if the user has no bookings).
    """
    bookings = load_bookings()
    return [b for b in bookings if b["user_id"] == user_id]


def cancel_booking(user_id, booking_id):
    """
    Cancel (delete) a booking for a user.

    - Looks for a booking matching both user_id and booking_id.
    - Removes it from the list.
    - Saves the updated list back into bookings.json.
    - Returns:
        True → if a booking was found and removed.
        False → if no such booking existed (nothing to cancel).
    """

    bookings = load_bookings()
    initial_len = len(bookings)

    bookings = [
        b
        for b in bookings
        if not (b["user_id"] == user_id and b["booking_id"] == booking_id)
    ]

    if len(bookings) < initial_len:  # Booking was successfully removed
        save_bookings(bookings)
        return True
    return False


def is_listing_available(listing_id, check_in, check_out):
    """
    Check if a given listing is available for the requested date range.

    Process:
    1. Load all bookings from the system.
    2. Convert the requested check-in/check-out strings into date objects.
    3. For each existing booking of the same listing:
        - Convert its check-in/check-out to dates.
        - Compare with the requested range.
        - If the date ranges overlap → return False (not available).
    4. If no overlaps are found → return True (listing is free).

    """

    bookings = load_bookings()
    requested_start = datetime.strptime(check_in, "%Y-%m-%d").date()
    requested_end = datetime.strptime(check_out, "%Y-%m-%d").date()

    for b in bookings:
        if b["listing_id"] != listing_id:
            continue  # Skip bookings for other listings

        existing_start = datetime.strptime(b["check_in"], "%Y-%m-%d").date()
        existing_end = datetime.strptime(b["check_out"], "%Y-%m-%d").date()

        if requested_start <= existing_end and requested_end >= existing_start:
            return False  # Overlap found → not available

    return True  # No overlaps → available


"""
Booking Workflow Summary:

1. Check availability:
   - Use is_listing_available() to verify that the requested dates are not already taken.

2. Create a booking:
   - If available, use create_booking() to add it to bookings.json.

3. View bookings:
   - Users can call get_user_bookings() to see all of their reservations.

4. Cancel a booking:
   - Use cancel_booking() to remove a booking (if it exists).

All booking information is permanently stored in bookings.json,
so the system remembers reservations even after restarting the app.
"""
