import csv

csv_file = "outreach_log.csv"

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)

with open(csv_file, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)

import os
import shutil

docs_dir = "docs"

for name in os.listdir(docs_dir):
    folder = os.path.join(docs_dir, name)
    if os.path.isdir(folder):
        shutil.rmtree(folder)