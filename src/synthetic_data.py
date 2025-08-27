import json
import pandas as pd
import requests
import re

# Import configuration variables for file paths and model name
from config import (
    MODEL,
    SYNTHETIC_LISTING_CSV_PATH,
    CLEANED_LISTING_CSV_PATH,
    MERGED_LISTING_CSV_PATH,
)


def extract_json(text):
    """
    This function tries to pull out the first valid JSON object or array from a string.
    It's handy for dealing with LLM outputs that might have extra text around the actual JSON.
    First, let's see if there's a JSON array in the text.
    """

    match = re.search(r"(\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            # If the JSON is a bit messy, we'll trim it until it works.
            temp = match.group(1)
            while temp:
                try:
                    return json.loads(temp)
                except json.JSONDecodeError:
                    temp = temp[:-1]
    # If no array, maybe there's a JSON object instead.
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            temp = match.group(1)
            while temp:
                try:
                    return json.loads(temp)
                except json.JSONDecodeError:
                    temp = temp[:-1]
    # If we get here, there was no valid JSON found.
    raise ValueError("No valid JSON could be extracted from LLM output.")


def generate_synthetic_listings(prompt, api_key):
    # This function sends a prompt to the LLM API and gets a synthetic property listing response.
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 5000,
        "temperature": 0.7,
    }
    # Make the API call and check for errors.
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    res_json = response.json()

    try:
        output_text = res_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise ValueError(f"Unexpected LLM response format: {res_json}")

    print("Raw LLM output:", output_text)  # Debug print

    # Return the cleaned-up output text.
    return output_text.strip()


def save_synthetic_listings(
    raw_output,
    filename=SYNTHETIC_LISTING_CSV_PATH,
):
    # This function takes the raw LLM output, extracts the listings, and saves them as a CSV.
    try:
        print("Raw output:", raw_output)
        listings = extract_json(raw_output)
        print("Extracted listings:", listings)
        print("Type of listings:", type(listings))
        if isinstance(listings, str):
            listings = json.loads(listings)
        if not isinstance(listings, list) or len(listings) == 0:
            raise ValueError("No valid listings extracted from LLM output.")
    except Exception as e:
        raise ValueError(f"LLM output is not valid JSON: {e}")
    # Convert the listings to a DataFrame for easy CSV export.
    df = pd.DataFrame(listings)
    print("DataFrame shape:", df.shape)
    if df.empty:
        raise ValueError("DataFrame is empty. Check extracted listings format.")
    df.to_csv(filename, index=False)
    print(f"Synthetic listings saved to {filename}")


def merge_with_real_listings(
    real_file=CLEANED_LISTING_CSV_PATH,
    synthetic_file=SYNTHETIC_LISTING_CSV_PATH,
    output_file=MERGED_LISTING_CSV_PATH,
):
    # This function merges the real and synthetic listings into one CSV file.
    df_real = pd.read_csv(real_file)
    df_synth = pd.read_csv(synthetic_file)
    if df_synth.empty:
        raise ValueError("Synthetic listings CSV is empty. Cannot merge.")
    # Combine both DataFrames and save the result.
    df_merged = pd.concat([df_real, df_synth], ignore_index=True)
    df_merged.to_csv(output_file, index=False)
    print("Merged listings saved to merged_listings.csv")


# Example prompt for generating synthetic listings with the LLM.
"""
Generate 10 fake property listings in Ontario under $500/night. 
Output as a JSON array of objects. Each object must have the following fields exactly as in my CSV:
- name: string
- location: string
- property_type: string (e.g., entire condo, entire rental unit, apartment)
- accommodates: integer
- amenities: string listing amenities separated by commas
- price: float (under 200)
- min_nights: integer
- max_nights: integer
- review_rating: float between 1.0 and 5.0
- tags: string, keywords separated by commas.
"""
