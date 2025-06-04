import requests
import json
import time

deepseek_api_keys = [
    "sk-9fe007791b4a40fc9c630caf5deb099a",
    "sk-e48ac8bbde3043828d867e84a73759e8",
    "sk-3b7f20df8e1b4cc9aad3f5792a015190",
    "sk-74f1a97d781c4f8b8f4bade035724edd"
]

def get_next_key():
    while True:
        for key in deepseek_api_keys:
            yield key

key_generator = get_next_key()

def edit_html_with_deepseek(info, html):
    for _ in range(len(deepseek_api_keys)):
        api_key = next(key_generator)
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a web developer who customizes HTML websites."},
                        {"role": "user", "content": f"Here is some business info:\n{info}\n\nNow customize the HTML site accordingly."},
                        {"role": "user", "content": html}
                    ],
                    "temperature": 0.7
                },
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ Key failed ({api_key[:8]}...): {response.status_code} - {response.text}")
                time.sleep(2)
        except Exception as e:
            print(f"❌ DeepSeek error with key {api_key[:8]}...: {e}")
            time.sleep(2)
    print("🚫 All keys failed for this request.")
    return None

def delete_folder(folder_path):
    import shutil, os
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
