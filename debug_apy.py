# debug_api.py

import json
import requests
from pathlib import Path


def load_config():
    """Loads the config.json file."""
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found!")
        return None
    with open(config_path, "r") as f:
        return json.load(f)


def run_test():
    """
    Makes a single API call and saves the full response to a file.
    """
    config = load_config()
    if not config:
        return

    access_token = config.get("access_token")
    alation_url = config.get("alation_url")

    if not access_token or not alation_url:
        print("❌ access_token or alation_url is missing from config.json")
        return

    # Using the exact endpoint we know contains the data
    url = f"{alation_url.rstrip('/')}/integration/v2/document/?deleted=false&limit=1000&skip=0"
    headers = {
        "TOKEN": access_token,
        "accept": "application/json"
    }

    print(f"▶️  Running test against: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:
            data = response.json()
            # 1. Print the total number of documents returned
            print(f"✅ SUCCESS: API returned {len(data)} documents.")

            # 2. Save the full, raw output to a new file
            output_filename = "debug_output.json"
            with open(output_filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Full response saved to: {output_filename}")

        else:
            print(f"❌ FAILED with status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_test()