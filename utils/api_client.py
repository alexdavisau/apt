# utils/api_client.py

import requests
import time
import json
import os
from datetime import datetime, timedelta

DOCUMENTS_CACHE_PATH = os.path.join('cache', 'cached_documents.json')
TEMPLATES_CACHE_PATH = os.path.join('cache', 'cached_templates.json')


def _make_api_request_with_retry(method, url, config, headers=None, payload=None, token_refresher=None,
                                 log_callback=print):
    """A centralized function to make API requests with retry logic for token expiration."""
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    token = config.get('token')
    if token:
        # Added .strip() for robustness against leading/trailing whitespace
        headers['Authorization'] = f"Token {token.strip()}"

    for attempt in range(2):
        try:
            response = requests.request(method, url, headers=headers, json=payload, timeout=60)

            if response.status_code == 401 and token_refresher and attempt == 0:
                log_callback("⚠️ API returned 401 Unauthorized. Attempting to refresh token...")
                is_refreshed, refresh_message = token_refresher(config)
                log_callback(refresh_message)

                if is_refreshed:
                    headers['Authorization'] = f"Token {config['token'].strip()}"
                    log_callback("✅ Token refreshed. Retrying the API request...")
                    continue
                else:
                    log_callback("❌ Token refresh failed. Aborting API request.")
                    return None

            if response.status_code != 403:
                response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as http_err:
            log_callback(f"❌ HTTP error occurred: {http_err} - {response.text}")
            return response
        except requests.exceptions.RequestException as req_err:
            log_callback(f"❌ A critical request error occurred: {req_err}")
            return None
    return None


def get_all_documents(config: dict, log_callback=print, force_api_fetch=False) -> list:
    """Fetches all documents, using cache if available and not expired."""
    from utils.token_checker import refresh_access_token

    cache_file = DOCUMENTS_CACHE_PATH
    # ... (rest of function is unchanged)
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback)
    # ...
    return []  # return empty list on failure


def get_all_templates(config: dict, log_callback=print, force_api_fetch=False) -> list:
    """Fetches all templates, using cache if available."""
    from utils.token_checker import refresh_access_token

    cache_file = TEMPLATES_CACHE_PATH
    # ... (rest of function is unchanged)
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback)
    # ...
    return []  # return empty list on failure


def create_documents_in_bulk(config: dict, payloads: list, job_name: str, log_callback=print, on_success_callback=None):
    """Posts a list of document payloads to the bulk creation API."""
    from utils.token_checker import refresh_access_token

    # ... (rest of function is unchanged)
    response = _make_api_request_with_retry("POST", url, config, payload=payloads, token_refresher=refresh_access_token,
                                            log_callback=log_callback)
    # ...


def get_hub_details(config: dict, hub_id: int, log_callback=print):
    """Fetches the full details of a specific document hub."""
    from utils.token_checker import refresh_access_token

    # ... (rest of function is unchanged)
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback)
    # ...
    return None  # return None on failure