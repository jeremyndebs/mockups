import csv

input_file = "outreach_log.csv"
output_file = "outreach_log_no_videographers.csv"

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, "w", newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        msg = row["WhatsApp Message"].lower()
        url = row["Mockup URL"].lower()
        if "videographer" not in msg and "videographer" not in url:
            writer.writerow(row)

print("✅ Done. Saved to outreach_log_no_videographers.csv")