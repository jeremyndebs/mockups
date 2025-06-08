import os
import csv
import subprocess
import pandas as pd
from deepseek_editor import edit_html_with_deepseek, delete_folder

TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
REPO_DIR = os.getcwd()
DEPLOY_DIR = os.path.join(REPO_DIR, "docs")
CSV_LOG = os.path.join(REPO_DIR, "outreach_log.csv")

scraped_leads = []
contacted_numbers = set()

# Load already contacted numbers to skip duplicates
if os.path.exists(CSV_LOG):
    with open(CSV_LOG, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contacted_numbers.add(row["Phone"])

# Load leads from businesses_without_websites.csv
if os.path.exists("businesses_without_websites.csv"):
    df = pd.read_csv("businesses_without_websites.csv")
    for _, row in df.iterrows():
        phone = str(row.get("phone", "")).strip()
        if pd.notna(phone) and phone not in contacted_numbers:
            raw_type = str(row.get("type") or row.get("services") or "general").lower().strip().replace(" ", "-")
            scraped_leads.append({
                "name": row.get("name", "Unknown"),
                "type": raw_type,
                "location": row.get("location", "Cape Town"),
                "phone": phone,
                "services": row.get("services", raw_type)
            })
    print(f"✅ Loaded {len(scraped_leads)} new leads from CSV.")
else:
    print("❌ businesses_without_websites.csv not found.")

# Prepare CSV to store only fresh contacts
outreach_rows = []

for lead in scraped_leads:
    folder_slug = lead['name'].lower().replace(" ", "-")
    folder_path = os.path.join(DEPLOY_DIR, folder_slug)
    template_file = os.path.join(TEMPLATE_DIR, f"{lead['type']}.html")

    if not os.path.exists(template_file):
        print(f"❌ No template for type: {lead['type']}")
        continue

    with open(template_file, "r", encoding="utf-8") as f:
        template_html = f.read()

    template_html = template_html.replace("href=\"http", "#")
    template_html = template_html.replace("href=\"https", "#")
    template_html = template_html.replace("Download", "Made by Jeremy Hill")

    info = f"""
    Business Name: {lead['name']}
    Services: {lead['services']}
    Location: {lead['location']}
    Contact: {lead['phone']}
    Type: {lead['type']}
    """

    custom_html = edit_html_with_deepseek(info, template_html)
    if not custom_html:
        print(f"❌ Skipped {lead['name']} due to DeepSeek fail")
        continue

    delete_folder(folder_path)
    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(custom_html)

    print(f"✅ Mockup for {lead['name']} ready.")

    slug = lead['name'].lower().replace(" ", "-")
    url = f"https://jeremyndebs.github.io/mockups/{slug}/"
    message = f"Hi {lead['name']}, I made you a sample site: {url} — I can hand it over for R2,500 if you're interested. Let me know. 😊"
    outreach_rows.append([lead['name'], lead['phone'], url, message])

# Git auto commit
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Deploy working mockups"])
subprocess.run(["git", "push", "origin", "master"])

# Save fresh outreach rows only
with open(CSV_LOG, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if os.stat(CSV_LOG).st_size == 0:
        writer.writerow(["Business Name", "Phone", "Mockup URL", "WhatsApp Message"])
    for row in outreach_rows:
        print(f"📲 Logging: {row[0]} | {row[1]} | {row[2]}")
        writer.writerow(row)
