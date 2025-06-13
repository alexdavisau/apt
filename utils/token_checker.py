import requests
import json
from pathlib import Path
from config import config_handler

CONFIG_PATH = Path("config.json")

# =====================================================================================
# The generic API request helper now lives here to resolve circular dependencies.
# =====================================================================================
def _make_api_request_with_retry(method: str, url: str, config: dict, token_refresher: callable, json_data: dict = None,
                                 params: dict = None, timeout: int = 30, log_callback=print):
    """
    Helper function to make an API request with token refresh retry logic.
    Receives the token_refresher function as an argument.
    """
    retries = 1

    while retries >= 0:
        headers = {"TOKEN": config["access_token"], "accept": "application/json"}
        if method == "POST":
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)

            if response.status_code in (401, 403) and retries > 0:
                log_callback("⚠️ Access token unauthorized. Attempting to refresh...")
                success, msg, new_tokens = token_refresher(config, log_callback=log_callback)
                if success:
                    config.update(new_tokens)
                    config_handler.save_config(CONFIG_PATH, config)
                    log_callback("✅ Token refreshed. Retrying API request...")
                    retries -= 1
                    continue
                else:
                    log_callback(f"❌ Failed to refresh token during API call: {msg}.")
                    return None  # Refresh failed, stop trying
            else:
                return response

        except requests.RequestException as e:
            log_callback(f"❌ Request failed: {e}")
            if retries > 0:
                log_callback("Retrying API call...")
                retries -= 1
                continue
            return None # Retries exhausted

    return None # Should not be reached, but included for safety


def refresh_access_token(config: dict, log_callback=print) -> tuple[bool, str, dict]:
    """
    Attempts to refresh the Alation access token using the refresh token.
    """
    alation_url = config.get("alation_url")
    refresh_token = config.get("refresh_token")
    user_id = config.get("user_id")

    if not alation_url or not refresh_token or user_id is None:
        return False, "Config missing URL, Refresh Token, or User ID.", {}

    url = f"{alation_url.rstrip('/')}/integration/v1/createAPIAccessToken/"
    payload = {"refresh_token": refresh_token, "user_id": user_id}

    log_callback("Attempting to refresh access token...")

    def no_op_refresher(*args, **kwargs):
        return False, "Already in refresh process.", {}

    response = _make_api_request_with_retry("POST", url, config, token_refresher=no_op_refresher, json_data=payload, log_callback=log_callback)

    if response and response.status_code in (200, 201):
        new_tokens = response.json()
        new_access_token = new_tokens.get("api_access_token")

        if new_access_token:
            log_callback("✅ Access token refreshed successfully.")
            new_refresh_token = new_tokens.get("refresh_token", refresh_token)
            return True, "Access token refreshed.", {"access_token": new_access_token, "refresh_token": new_refresh_token, "user_id": user_id}
        else:
            return False, "Refresh successful but no new token found.", {}
    elif response:
        return False, f"Refresh failed with status {response.status_code}: {response.text}", {}
    else:
        return False, "Connection error during token refresh.", {}


def check_token(config: dict) -> tuple[bool, str]:
    """
    Checks if the API token is valid. If not, attempts to refresh it.
    """
    log_message = print
    if not config.get("alation_url") or not config.get("access_token"):
        return False, "❌ Config missing URL or Access Token."

    url = f"{config['alation_url'].rstrip('/')}/integration/v1/user/"
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token, log_callback=log_message)

    if response and response.status_code == 200:
        return True, "✅ Token is valid."
    elif response:
        return False, f"❌ Token is invalid (Status: {response.status_code}). Check logs for refresh attempt details."
    else:
        # This is the error you were seeing. It means the helper returned None.
        return False, "❌ Connection Error during token check (no response after retries)."