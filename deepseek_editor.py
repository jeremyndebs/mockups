import requests
import time
import shutil
import os

API_KEYS = [
    "sk-9fe007791b4a40fc9c630caf5deb099a",
    "sk-e48ac8bbde3043828d867e84a73759e8",
    "sk-3b7f20df8e1b4cc9aad3f5792a015190",
]

def edit_html_with_deepseek(business_info, html_template):
    prompt = (
        f"You are a web developer. Use the following business info to update the HTML template:\n"
        f"{business_info}\n\n"
        f"Only change the text content to reflect the business info. Do not change layout or styles.\n\n"
        f"HTML template:\n{html_template}"
    )

    for key in API_KEYS:
        try:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a web developer customizing a business website."},
                    {"role": "user", "content": prompt}
                ]
            }

            print(f"🔁 Using API key: {key[:10]}...")

            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                print(f"⚠️ Rate limited on key {key[:10]}... switching.")
                time.sleep(2)
                continue
            else:
                print(f"❌ Error from DeepSeek: {response.status_code} - {response.text}")
                continue

        except Exception as e:
            print(f"❌ Exception with key {key[:10]}: {e}")
            continue

    print("❌ All keys failed or rate-limited.")
    return None

def delete_folder(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"❌ Failed to delete folder {path}: {e}")
