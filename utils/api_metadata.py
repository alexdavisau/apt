# utils/api_metadata.py

import requests

def get_custom_fields(config: dict) -> dict: # Pass config dict
    """
    Retrieves custom field definitions from the Alation API.
    Uses the TOKEN header for consistency with other API calls.
    """
    alation_url = config.get("alation_url")
    access_token = config.get("access_token")

    if not alation_url or not access_token:
        print("❌ Alation URL or Access Token missing in config for get_custom_fields.")
        return None

    url = f"{alation_url.rstrip('/')}/openapi/custom_fields/v1"
    headers = {
        "TOKEN": access_token, # Changed from "Authorization: Bearer" to "TOKEN"
        "accept": "application/json"
    }

    print(f"🔍 Fetching custom fields from {url} using TOKEN header...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Retrieved custom fields.")
            return response.json()
        else:
            print(f"❌ Failed to get custom fields: {response.status_code} {response.text}")
            return None
    except requests.RequestException as e:
        print(f"❌ Error fetching custom fields: {e}")
        return None