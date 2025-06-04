import requests
import csv

# Your Google Places API Key
API_KEY = "AIzaSyDIcE2rmT88K6RFM0dDQ-JhRNrGG-vkpuA"

# Business categories to search for
business_types = ["plumber", "electrician", "mechanic", "handyman", "personal trainer"]

# Search location
location = "Cape Town"

# Output CSV file
csv_filename = "businesses_without_websites.csv"

# Google Places Text Search API URL
BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Function to search for businesses
def search_businesses(business_type):
    url = f"{BASE_URL}?query={business_type}+in+{location}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    results = []

    for business in data.get("results", []):
        name = business.get("name", "N/A")
        address = business.get("formatted_address", "N/A")
        place_id = business.get("place_id")

        # Get more details about the business
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website&key={API_KEY}"
        details_response = requests.get(details_url)
        details_data = details_response.json()
        details = details_data.get("result", {})

        phone_number = details.get("formatted_phone_number", "N/A")
        website = details.get("website", None)

        # Only include businesses with NO website
        if not website:
            results.append([name, address, phone_number])

    return results

# Collect results for all business types
all_results = []
for business_type in business_types:
    print(f"Searching for {business_type}s in {location}...")
    results = search_businesses(business_type)
    all_results.extend(results)

# Save to CSV file
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Business Name", "Address", "Phone Number"])
    writer.writerows(all_results)

print(f"Done! Results saved to {csv_filename}")
