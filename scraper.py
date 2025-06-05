import os
import csv
import subprocess
from deepseek_editor import edit_html_with_deepseek, delete_folder
from main import search_businesses as scrape_businesses

TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
REPO_DIR = os.getcwd()
DEPLOY_DIR = os.path.join(REPO_DIR, "docs")
CSV_LOG = os.path.join(REPO_DIR, "outreach_log.csv")

scraped_leads = []
for business_type in ["plumber", "pet groomer", "accountant", "photographer"]:
    scraped_leads.extend(scrape_businesses(business_type)[:15])

print(f"✅ {len(scraped_leads)} leads scraped for mockup")

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

# Git auto commit
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Deploy working mockups"])
subprocess.run(["git", "push", "origin", "master"])

# Log WhatsApp message
with open(CSV_LOG, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if os.stat(CSV_LOG).st_size == 0:
        writer.writerow(["Business Name", "Phone", "Mockup URL", "WhatsApp Message"])

    for lead in scraped_leads:
        slug = lead['name'].lower().replace(" ", "-")
        url = f"https://jeremyndebs.github.io/mockups/{slug}/"
        message = f"Hi {lead['name']}, I made you a sample site: {url} — I can hand it over for R2,500 if you're interested. Let me know. 😊"
        print(f"📲 Logging: {lead['name']} | {lead['phone']} | {url}")
        writer.writerow([lead['name'], lead['phone'], url, message])
