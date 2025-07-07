import requests
import csv
import time

API_KEY = "AIzaSyA7QtlkGAJix9fNiBaYoQ3sHD9ArU7hxUI"
INPUT_CSV = "businesses_without_websites.csv"
OUTPUT_CSV = "businesses_with_real_numbers.csv"

def get_place_id(name, address):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{name} {address}",
        "inputtype": "textquery",
        "fields": "place_id",
        "key": API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    candidates = data.get("candidates", [])
    if candidates:
        return candidates[0].get("place_id")
    return None

def get_phone_number(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number",
        "key": API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return data.get("result", {}).get("formatted_phone_number", "")

# Read all leads
with open(INPUT_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# Enrich with real phone numbers
for lead in leads:
    name = lead["name"]
    address = lead["location"]
    print(f"🔍 Searching for {name}...")
    place_id = get_place_id(name, address)
    if place_id:
        phone = get_phone_number(place_id)
        if phone:
            print(f"✅ Found phone: {phone}")
            lead["phone"] = phone
        else:
            print("❌ No phone found.")
    else:
        print("❌ No place_id found.")
    time.sleep(0.2)  # Be nice to the API

# Write updated leads to new CSV
with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=leads[0].keys())
    writer.writeheader()
    for row in leads:
        writer.writerow(row)

print("✅ Done. Check businesses_with_real_numbers.csv for results.")