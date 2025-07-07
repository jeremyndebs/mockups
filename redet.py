import os
import shutil
import csv

# 1. Clear outreach_log.csv (keep only the header)
log_csv = "outreach_log.csv"
header = ["Business Name", "Phone", "Mockup URL", "WhatsApp Message"]
with open(log_csv, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

# 2. Delete all mockup folders in docs/
docs_dir = "docs"
if os.path.exists(docs_dir):
    for name in os.listdir(docs_dir):
        folder = os.path.join(docs_dir, name)
        if os.path.isdir(folder):
            shutil.rmtree(folder)
print("✅ Cleared outreach log and deleted all mockup folders in docs/.")

# 3. Now run your main script as usual (it will only use businesses_without_websites.csv)
# python final.py