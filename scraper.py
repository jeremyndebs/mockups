import os
import csv
import subprocess
from main import search_businesses as scrape_businesses
from deepseek_editor import edit_html_with_deepseek, delete_folder

# === CONFIGURATION ===
TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
REPO_DIR = os.getcwd()
DEPLOY_DIR = os.path.join(REPO_DIR, "docs")
CSV_LOG = os.path.join(REPO_DIR, "outreach_log.csv")

# === SCRAPE LEADS DIRECTLY ===
business_types = ["plumber", "pet groomer", "accountant", "photographer"]
scraped_leads = []
for btype in business_types:
    leads = scrape_businesses(btype)
    scraped_leads.extend(leads[:15])  # cap per type
print(f"✅ Scraped {len(scraped_leads)} leads across types: {', '.join(business_types)}")

# === PROCESS EACH LEAD ===
outreach_rows = []
for lead in scraped_leads:
    name = lead.get('name')
    phone = lead.get('phone')
    btype = lead.get('type')
    folder_slug = name.lower().replace(" ", "-")
    folder_path = os.path.join(DEPLOY_DIR, folder_slug)
    template_file = os.path.join(TEMPLATE_DIR, f"{btype}.html")

    if not os.path.exists(template_file):
        print(f"❌ No template for type '{btype}' for {name}")
        continue

    with open(template_file, 'r', encoding='utf-8') as f:
        template_html = f.read()
    # remove external links + brand
    template_html = template_html.replace('href="http', '#')
    template_html = template_html.replace('href="https', '#')
    template_html = template_html.replace('Download', 'Made by Jeremy Hill')

    info = f"""
Business Name: {name}
Services: {lead.get('services')}
Location: {lead.get('location')}
Contact: {phone}
Type: {btype}
"""
    custom_html = edit_html_with_deepseek(info, template_html)
    if not custom_html:
        print(f"❌ DeepSeek failed for {name}")
        continue

    delete_folder(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(custom_html)
    print(f"✅ Mockup created for {name}")

    url = f"https://jeremyndebs.github.io/mockups/{folder_slug}/"
    message = f"Hi {name}, I made you a sample site: {url} — I can hand it over for R2,500 if you're interested. Let me know. 😊"
    outreach_rows.append([name, phone, url, message])

# === DEPLOY TO GITHUB ===
subprocess.run(["git", "add", "docs/"])
subprocess.run(["git", "commit", "-m", "Deploy mockups"])
subprocess.run(["git", "push", "origin", "master"])

# === WRITE OUTREACH LOG ===
with open(CSV_LOG, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    if os.stat(CSV_LOG).st_size == 0:
        writer.writerow(["Business Name", "Phone", "Mockup URL", "WhatsApp Message"])
    for row in outreach_rows:
        print(f"📲 Logging: {row[0]} | {row[1]} | {row[2]}")
        writer.writerow(row)
