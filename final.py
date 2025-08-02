import requests
import csv
import time
import os
import shutil
import argparse
import re

API_KEY = "AIzaSyA7QtlkGAJix9fNiBaYoQ3sHD9ArU7hxUI"
LOCATION = "-33.9249,18.4241"  # Cape Town lat/lng
RADIUS = 15000
TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
DEPLOY_DIR = os.path.join(os.getcwd(), "docs")
LOG_CSV = os.path.join(os.getcwd(), "outreach_log.csv")
LEADS_CSV = os.path.join(os.getcwd(), "businesses_without_websites.csv")

DEFAULT_TYPES = ["Solar Panel Installers", "Borehole Drillers", "Videographers", "Flooring Installers",]
DEFAULT_MESSAGE = (
    "Hey,\n\n"
    "I'm a freelance web developer and I noticed your business doesn’t have a website — so I built a custom one for you:\n\n"
    "👉 {url}\n\n"
    "It's tailored for {type} in Cape Town and optimized to help you bring in more customers and show up in Google.\n\n"
    "If you like it, I can launch it for just R2,500 — one-time payment, no monthly fees unless you want ongoing updates or hosting.\n\n"
    "Let me know what you think — happy to tweak it for you too 👍\n\n"
    "— Jeremy Hill\n"
    "Freelance Web Developer"
)

def search_google(search_terms, max_results=500):
    print("Starting Google scraping with Business API...")
    results = []
    for term in search_terms:
        print(f"🔍 Searching for: {term}")
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id"
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
                for place in data["places"]:
                    if len(results) >= max_results:
                        break
                    name = place.get("displayName", {}).get("text", f"Unknown {term.title()}")
                    address = place.get("formattedAddress", "Cape Town")
                    place_id = place.get("id") or place.get("place_id")
                    phone = ""
                    # --- Get real phone number using Place Details API ---
                    if place_id:
                        details_url = (
                            f"https://maps.googleapis.com/maps/api/place/details/json"
                            f"?place_id={place_id}&fields=formatted_phone_number"
                            f"&key={API_KEY}"
                        )
                        try:
                            details_resp = requests.get(details_url)
                            details_data = details_resp.json()
                            phone = details_data.get("result", {}).get("formatted_phone_number", "")
                        except Exception as e:
                            print(f"❌ Error fetching phone for {name}: {e}")
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
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error fetching {term}: {e}")
                break
        if len(results) >= max_results:
            break
    # Save to CSV
    with open(LEADS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "type", "location", "phone", "services"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"✅ Scraped {len(results)} results.")
    return results

def read_unique_leads(csv_file):
    leads = []
    seen_phones = set()
    if not os.path.exists(csv_file):
        return leads
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = row["phone"]
            if phone and phone not in seen_phones:
                leads.append(row)
                seen_phones.add(phone)
    return leads

def get_contacted_phones(log_csv):
    contacted = set()
    if os.path.exists(log_csv):
        with open(log_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacted.add(row["Phone"])
    return contacted

def make_mockup_and_log(lead, writer, outreach_message):
    import re

    slug = re.sub(r'[^a-z0-9\-]', '', lead["name"].lower().replace(" ", "-"))
    folder_path = os.path.join(DEPLOY_DIR, slug)
    template_dir = os.path.join(TEMPLATE_DIR, lead['type'])

    if not os.path.exists(template_dir):
        print(f"❌ Missing template for {lead['type']}")
        return

    # Remove old mockup if exists
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

    # Copy all files/folders from template, replacing text in text files
    for root, dirs, files in os.walk(template_dir):
        rel_path = os.path.relpath(root, template_dir)
        dest_dir = os.path.join(folder_path, rel_path) if rel_path != "." else folder_path
        os.makedirs(dest_dir, exist_ok=True)
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            # Only replace text in .html, .txt, .js, .css files
            if file.lower().endswith(('.html', '.htm', '.txt', '.js', '.css')):
                with open(src_file, "r", encoding="utf-8") as fsrc:
                    content = fsrc.read()
                content = content.replace("[Business Name]", lead["name"])
                content = content.replace("[Phone]", lead["phone"])
                content = content.replace("[Address]", lead["location"])
                with open(dest_file, "w", encoding="utf-8") as fdst:
                    fdst.write(content)
            else:
                shutil.copy2(src_file, dest_file)

    url = f"https://jeremyndebs.github.io/mockups/{slug}/"
    msg = outreach_message.format(
        name=lead['name'],
        url=url,
        phone=lead['phone'],
        address=lead['location'],
        services=lead['services'],
        type=lead['type']
    )
    writer.writerow([lead['name'], lead['phone'], url, msg])
    print(f"✅ Mockup ready + outreach message generated for {lead['name']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape, mockup, and outreach for businesses.")
    parser.add_argument("--types", nargs="+", default=DEFAULT_TYPES, help="Business types to target (e.g. plumber photographer)")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Outreach message. Use {name}, {url}, {phone}, {address}, {services}, {type} as placeholders.")
    parser.add_argument("--max", type=int, default=500, help="Max results per type")
    args = parser.parse_args()

    # 1. Scrape leads and get real phone numbers from Google
    leads = search_google(args.types, max_results=args.max)

    # 2. Remove duplicates and filter out already-contacted
    unique_leads = read_unique_leads(LEADS_CSV)
    contacted = get_contacted_phones(LOG_CSV)
    fresh_leads = [lead for lead in unique_leads if lead["phone"] and lead["phone"] not in contacted]
    print(f"🚀 Found {len(fresh_leads)} new leads to process.")

    # 3. Generate mockups and outreach messages
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if os.stat(LOG_CSV).st_size == 0:
            writer.writerow(["Business Name", "Phone", "Mockup URL", "WhatsApp Message"])
        for lead in fresh_leads:
            make_mockup_and_log(lead, writer, args.message)

    print("🚀 All done. Mockups and outreach messages generated.")