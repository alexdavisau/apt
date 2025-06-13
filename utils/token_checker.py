# utils/token_checker.py

import requests
from datetime import datetime
import os


def check_token(config: dict) -> (bool, str):
    """
    Checks if the API token is valid by making a simple API call.
    """
    # Local import to prevent circular dependency
    from utils.api_client import _make_api_request_with_retry

    if not config.get('token'):
        return False, "❌ Token is missing from config.json."

    base_url = config['alation_url'].rstrip('/')
    url = f"{base_url}/integration/v1/user/"

    # Note: We pass a simple print function for the log_callback here to avoid complexities
    response = _make_api_request_with_retry("GET", url, config, log_callback=print)

    if response and response.status_code == 200:
        return True, "✅ Token is valid."
    elif response:
        # Combine the error messages into one string to return only 2 values.
        error_details = response.text
        return False, f"❌ Token is likely invalid. API returned: {response.status_code} - {error_details}"
    else:
        return False, "❌ Failed to connect to Alation. Check URL and network."


def refresh_access_token(config: dict) -> (bool, str):
    """
    Refreshes the API token using the refresh_token from the config file.
    """
    from utils.api_client import _make_api_request_with_retry

    refresh_token = config.get("refresh_token")
    if not refresh_token:
        return False, "❌ refresh_token is missing from config.json. Cannot refresh."

    base_url = config['alation_url'].rstrip('/')
    url = f"{base_url}/integration/v1/accessToken/"
    payload = {"refresh_token": refresh_token}

    # Use a simple print callback to avoid circular dependencies with main_window logging
    response = _make_api_request_with_retry("POST", url, config, payload=payload, log_callback=print)

    if response and response.status_code == 200:
        data = response.json()
        config['token'] = data['token']
        config['user_id'] = data['user_id']

        # Save the updated config back to the file
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            return True, f"✅ New API Token for user_id {data['user_id']} obtained and saved."
        except Exception as e:
            return False, f"❌ Failed to save new token to config.json: {e}"
    elif response:
        return False, f"❌ API call to refresh token failed with status {response.status_code}: {response.text}"
    else:
        return False, "❌ Failed to connect to Alation to refresh token."