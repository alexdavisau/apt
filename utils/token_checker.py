import json
from pathlib import Path

# NEW IMPORT: Import the centralized API request helper from api_client
from utils.api_client import _make_api_request_with_retry

# config_handler is needed by refresh_access_token (and by check_token to save config)
from config import config_handler

# Assuming config.json is at the project root for saving
CONFIG_PATH = Path("config.json")


def refresh_access_token(config: dict, log_callback=print) -> tuple[bool, str, dict]:
    """
    Attempts to refresh the Alation access token using the refresh token.
    This function is passed as token_refresher to _make_api_request_with_retry.
    """
    alation_url = config.get("alation_url")
    refresh_token = config.get("refresh_token")
    user_id = config.get("user_id")

    if not alation_url or not refresh_token or user_id is None:
        log_callback("❌ Config missing URL, Refresh Token, or User ID for refresh.")
        return False, "Config missing URL, Refresh Token, or User ID.", {}

    url = f"{alation_url.rstrip('/')}/integration/v1/createAPIAccessToken/"
    payload = {
        "refresh_token": refresh_token,
        "user_id": user_id
    }

    log_callback("Attempting to refresh access token...")

    # When refresh_access_token calls _make_api_request_with_retry internally,
    # it must NOT pass itself as the token_refresher to prevent infinite loop.
    # Pass a no-op function for this specific internal call.
    def no_op_refresher(*args, **kwargs):
        log_callback("DEBUG: Preventing recursive refresh attempt in refresh_access_token's internal API call.")
        return False, "Already in refresh process.", {}

    response = _make_api_request_with_retry("POST", url, config, token_refresher=no_op_refresher, json_data=payload,
                                            log_callback=log_callback)

    if response and response.status_code in (200, 201):
        new_tokens = response.json()
        new_access_token = new_tokens.get("api_access_token")

        if new_access_token:
            log_callback("✅ Access token refreshed successfully.")
            # Ensure user_id and refresh_token are kept if they weren't in new_tokens
            return True, "Access token refreshed.", {"access_token": new_access_token, "refresh_token": refresh_token,
                                                     "user_id": user_id}
        else:
            log_callback("❌ Refresh successful but no new api_access_token found in response.")
            return False, "Refresh successful but no new api_access_token found.", {}
    elif response and response.status_code in (401, 403):
        log_callback(
            f"❌ Refresh token unauthorized or invalid ({response.status_code}). Please re-authenticate manually.")
        return False, f"Refresh token unauthorized or invalid ({response.status_code}).", {}
    elif response:
        log_callback(f"⚠️ Unexpected response during token refresh: {response.status_code} {response.text}")
        return False, f"Unexpected response during token refresh: {response.status_code}.", {}
    else:
        return False, "Connection error during token refresh (no response after retries).", {}


def check_token(config: dict) -> tuple[bool, str]:
    """
    Checks if the API token is valid. If not, attempts to refresh it and then re-checks.
    Uses the centralized _make_api_request_with_retry helper from api_client.
    Returns a tuple: (bool: is_valid, str: message)
    """
    alation_url = config.get("alation_url")
    access_token = config.get("access_token")

    if not alation_url or not access_token:
        return False, "❌ Config missing URL or Access Token."

    url = f"{alation_url.rstrip('/')}/integration/v1/user/"

    log_message = print

    # Pass refresh_access_token as the token_refresher for this API call
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_message)

    if response and response.status_code == 200:
        return True, "✅ Token is valid."
    elif response and response.status_code in (401, 403):
        message = f"❌ Token is Unauthorized ({response.status_code}). Attempting to refresh..."
        log_message(message)

        # Attempt to refresh the token using refresh_access_token (which itself uses the helper)
        success, refresh_msg, new_tokens = refresh_access_token(config, log_callback=log_message)

        if success:
            config.update(new_tokens)
            config_handler.save_config(CONFIG_PATH, config)
            log_message("✅ Tokens updated and saved. Re-checking token validity with new token...")

            # Re-check the token with the newly obtained access token, using the helper
            re_check_response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                                             log_callback=log_message)

            if re_check_response and re_check_response.status_code == 200:
                return True, "✅ Token refreshed and now valid."
            elif re_check_response:
                return False, f"❌ Token refreshed but re-check failed ({re_check_response.status_code}). {re_check_response.text}"
            else:  # No response from re_check_response
                return False, "❌ Token refreshed but re-check failed (no response from API).", {}
        else:
            return False, f"❌ Token unauthorized ({response.status_code}). Refresh failed: {refresh_msg}. Please update config manually."
    elif response:
        return False, f"⚠️ Unexpected response during initial token check: {response.status_code}. Check URL/Token."
    else:  # No response from initial check
        return False, "❌ Connection Error during token check (no response after retries).", {}