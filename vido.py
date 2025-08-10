import os
import csv
import shutil

TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
DEPLOY_DIR = os.path.join(os.getcwd(), "mockups")  # Change to "docs" if needed
OUTREACH_CSV = "outreach_log.csv"

def slug_from_url(url):
    return url.rstrip("/").split("/")[-1]

def make_videographer_mockup(lead, slug):
    folder_path = os.path.join(DEPLOY_DIR, slug)
    template_path = os.path.join(TEMPLATE_DIR, "videographer", "index.html")
    if not os.path.exists(template_path):
        print(f"❌ Missing template for videographer ({template_path})")
        return
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(template_path, "r", encoding="utf-8") as tf:
        html = tf.read()
    html = html.replace("[Business Name]", lead["Business Name"])
    html = html.replace("[Phone]", lead["Phone"])
    html = html.replace("[Address]", "")  # Add address if available
    with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as out:
        out.write(html)
    print(f"✅ Mockup created for {lead['Business Name']} at {slug}")

with open(OUTREACH_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        msg = row["WhatsApp Message"].lower()
        url = row["Mockup URL"].lower()
        if "videographer" in msg or "videographer" in url:
            slug = slug_from_url(row["Mockup URL"])
            make_videographer_mockup(row, slug)