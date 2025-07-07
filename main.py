import requests
import csv
import time
import os
import shutil
import subprocess
import re

API_KEY = "AIzaSyA7QtlkGAJix9fNiBaYoQ3sHD9ArU7hxUI"
LOCATION = "-33.9249,18.4241"  # Cape Town lat/lng
RADIUS = 15000
TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
DEPLOY_DIR = os.path.join(os.getcwd(), "docs")
LOG_CSV = os.path.join(os.getcwd(), "outreach_log.csv")
LEADS_CSV = os.path.join(os.getcwd(), "businesses_without_websites.csv")

def search_google(search_terms, max_results=500):
    print("Starting Google scraping with Business API...")
    results = []
    for term in search_terms:
        print(f"🔍 Searching for: {term}")
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
        }
        payload = {
            "textQuery": f"{term} in Cape Town",
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": float(LOCATION.split(',')[0]),
                        "longitude": float(LOCATION.split(',')[1])
                    },
                    "radius": RADIUS
                }
            }
        }
        next_page_token = None
        term_results = 0
        while len(results) < max_results:
            if next_page_token:
                payload["pageToken"] = next_page_token
            else:
                payload.pop("pageToken", None)
            try:
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()
                if "places" not in data:
                    print(f"❌ API Error for '{term}': {data}")
                    break
                print(f"✅ API Response for '{term}': {len(data['places'])} results found.")
                for i, place in enumerate(data["places"]):
                    if len(results) >= max_results:
                        break
                    name = place.get("displayName", {}).get("text", f"Unknown {term.title()}")
                    address = place.get("formattedAddress", "Cape Town")
                    phone = f"08100000{(len(results) % 100):02d}"  # dummy placeholder
                    results.append({
                        "name": name,
                        "type": term,
                        "location": address,
                        "phone": phone,
                        "services": term
                    })
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
                time.sleep(2)  # Google recommends a short delay before using nextPageToken
            except Exception as e:
                print(f"❌ Error fetching {term}: {e}")
                break
        if len(results) >= max_results:
            break
    with open("businesses_without_websites.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "type", "location", "phone", "services"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"✅ Scraped {len(results)} results.")
    return results

# 1. Read unique leads from CSV (by phone)
leads = []
seen_phones = set()
with open(LEADS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        phone = row["phone"]
        if phone and phone not in seen_phones:
            leads.append(row)
            seen_phones.add(phone)

# 2. Filter out already-contacted leads
contacted = set()
if os.path.exists(LOG_CSV):
    with open(LOG_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacted.add(row["Phone"])

fresh_leads = [lead for lead in leads if lead["phone"] not in contacted]
print(f"🚀 Found {len(fresh_leads)} new leads to process.")

# 3. Generate mockups and outreach messages
with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if os.stat(LOG_CSV).st_size == 0:
        writer.writerow(["Business Name", "Phone", "Mockup URL", "WhatsApp Message"])

    for lead in fresh_leads:
        slug = re.sub(r'[^a-z0-9\-]', '', lead["name"].lower().replace(" ", "-"))
        folder_path = os.path.join(DEPLOY_DIR, slug)
        template_path = os.path.join(TEMPLATE_DIR, lead['type'], "index.html")
        if not os.path.exists(template_path):
            print(f"❌ Missing template for {lead['type']}")
            continue

        # Read and customize the template
        with open(template_path, "r", encoding="utf-8") as tf:
            html = tf.read()
        html = html.replace("[Business Name]", lead["name"])
        html = html.replace("[Address]", lead["location"])
        html = html.replace("[Phone]", lead["phone"])

        # Create the folder and save the customized HTML
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as out:
            out.write(html)

        url = f"https://jeremyndebs.github.io/mockups/{slug}/"
        msg = (
            f"Hello {lead['name']},\n"
            f"I have created a complimentary sample website for your business: {url}\n"
            f"If you are interested in acquiring this site or would like to discuss further, please let me know."
        )
        writer.writerow([lead['name'], lead['phone'], url, msg])
        print(f"✅ Mockup ready + outreach message generated for {lead['name']}")

print("🚀 All done. Mockups and outreach messages generated.")

if __name__ == "__main__":
    business_types = ["plumber", "pet groomer", "accountant", "photographer"]
    leads = search_google(business_types)
