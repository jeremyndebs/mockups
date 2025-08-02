import os
import csv
import shutil
import re

TEMPLATE_DIR = "C:/Users/DELL/Desktop/temps"
DEPLOY_DIR = os.path.join(os.getcwd(), "docs")
OUTREACH_CSV = "outreach_log.csv"

def get_lead_type_from_url(url):
    # crude guess: look for type in the outreach message or url
    if "plumber" in url:
        return "plumber"
    if "pet-groomer" in url or "pet" in url:
        return "pet groomer"
    if "accountant" in url:
        return "accountant"
    if "photographer" in url:
        return "photographer"
    if "videographer" in url:
        return "videographer"
    if "flooring" in url:
        return "flooring installers"
    if "borehole" in url:
        return "borehole drillers"
    if "solar" in url:
        return "solar panel installers"
    # fallback
    return "plumber"

def slug_from_url(url):
    # get the last part of the URL path
    return url.rstrip("/").split("/")[-1]

def regenerate_mockup(lead, lead_type, slug):
    folder_path = os.path.join(DEPLOY_DIR, slug)
    template_dir = os.path.join(TEMPLATE_DIR, lead_type)
    template_path = os.path.join(template_dir, "index.html")
    if not os.path.exists(template_path):
        print(f"❌ Missing template for {lead_type} ({template_path})")
        return
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(template_path, "r", encoding="utf-8") as tf:
        html = tf.read()
    html = html.replace("[Business Name]", lead["Business Name"])
    html = html.replace("[Phone]", lead["Phone"])
    html = html.replace("[Address]", "")  # Address not in outreach_log, can be blank or fetched if needed
    with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as out:
        out.write(html)
    print(f"✅ Regenerated mockup for {lead['Business Name']} at {slug}")

with open(OUTREACH_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row["Mockup URL"]
        slug = slug_from_url(url)
        folder_path = os.path.join(DEPLOY_DIR, slug)
        if not os.path.exists(folder_path) or not os.path.exists(os.path.join(folder_path, "index.html")):
            lead_type = get_lead_type_from_url(url)
            print(f"Regenerating: {row['Business Name']} | {lead_type} | {slug}")
            regenerate_mockup(row, lead_type, slug)