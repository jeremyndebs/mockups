import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

MAX_PER_TYPE = 15

def search_google(business_type):
    print(f"🔍 Scraping {business_type}s in Cape Town...")
    query = quote(f"{business_type} Cape Town site:facebook.com OR site:yellowpages.co.za OR site:snupit.co.za")
    url = f"https://www.google.com/search?q={query}&num=30"

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for result in soup.select("div.g"):
        if len(results) >= MAX_PER_TYPE:
            break

        text = result.get_text(" ", strip=True)
        name_match = re.search(r"^(.*?) -", text)
        phone_match = re.search(r"(\+27|0)[6-8][0-9]{8}", text)

        name = name_match.group(1) if name_match else f"Unknown {business_type.title()}"
        phone = phone_match.group(0) if phone_match else ""

        if phone:
            results.append({
                "name": name,
                "type": business_type,
                "location": "Cape Town",
                "phone": phone,
                "services": business_type
            })

    print(f"✅ Found {len(results)} {business_type}s")
    return results
