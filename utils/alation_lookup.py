import requests
import json
from urllib.parse import urljoin
# NEW IMPORT: Import the centralized API request helper from api_client
from utils.api_client import _make_api_request_with_retry
# The config_handler import is needed because _make_api_request_with_retry uses it internally.
from config import config_handler
from pathlib import Path

# Need to import refresh_access_token as it is passed as token_refresher
# This import has to be placed carefully to avoid circular dependency.
# Since refresh_access_token is part of the token_checker module,
# and token_checker imports api_client (which imports this helper),
# we need to be careful. A common pattern is to import it locally within functions that use it,
# or ensure token_checker imports api_client at the bottom of its file.
from utils.token_checker import refresh_access_token

CONFIG_PATH = Path("config.json")


def lookup_alation_object(config: dict, name_or_email: str, otype_hint: str = None, log_callback=print) -> dict:
    """
    Looks up an Alation user or group by name or email/display name using the correct API endpoints.
    Returns a dict {"otype": "user"|"groupprofile", "oid": <ID>} or None if not found.
    """
    base_url = config['alation_url'].rstrip('/')

    search_term = name_or_email.strip()
    if not search_term:
        log_callback("Lookup term is empty.")
        return None

    search_order = []
    if otype_hint == "user":
        search_order = ["user", "group"]
    elif otype_hint == "group":
        search_order = ["group", "user"]
    else:
        search_order = ["user", "group"]

    for obj_type in search_order:
        if obj_type == "user":
            url = f"{base_url}/integration/v1/user/"
            params = {"email": search_term, "limit": 100}  # Use 'email' parameter for exact match
            log_callback(f"🔍 Searching for user by email: '{search_term}' from {url} with params {params}...")
        elif obj_type == "group":
            url = f"{base_url}/integration/v1/group/"
            params = {"name": search_term, "limit": 100}  # Use 'name' parameter for groups
            log_callback(f"🔍 Searching for group by name: '{search_term}' from {url} with params {params}...")
        else:
            continue

        response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token, params=params,
                                                log_callback=log_callback)

        if response and response.status_code == 200:
            results = response.json()
            print("---TESTING DEBUG LINE PRESENCE---")  # Temporary debug line
            log_callback(
                f"DEBUG: Raw search results for '{search_term}' ({obj_type}): {json.dumps(results[:5], indent=2)}")
            if results:
                for res in results:
                    if obj_type == "user":
                        # FIX: Explicitly convert to string before lower() for robust comparison
                        if str(res.get('email', '')).lower() == search_term.lower():
                            log_callback(
                                f"DEBUG: Confirmed exact email match for '{search_term}' (ID: {res.get('id')}). FINAL RETURN.")
                            return {"otype": obj_type, "oid": res.get('id')}
                        elif str(res.get('display_name', '')).lower() == search_term.lower():
                            log_callback(
                                f"DEBUG: Confirmed exact display_name match for '{search_term}' (ID: {res.get('id')}). FINAL RETURN.")
                            return {"otype": obj_type, "oid": res.get('id')}
                        elif str(
                                f"{res.get('first_name', '')} {res.get('last_name', '')}".strip()).lower() == search_term.lower():
                            log_callback(
                                f"DEBUG: Confirmed exact full name match for '{search_term}' (ID: {res.get('id')}). FINAL RETURN.")
                            return {"otype": obj_type, "oid": res.get('id')}

                    elif obj_type == "group":
                        # FIX: Explicitly convert to string before lower() for robust comparison
                        if str(res.get('name', '')).lower() == search_term.lower() or \
                                str(res.get('display_name', '')).lower() == search_term.lower():
                            log_callback(
                                f"DEBUG: Confirmed exact group name/display_name match for '{search_term}' (ID: {res.get('id')}). FINAL RETURN.")
                            return {"otype": obj_type, "oid": res.get('id')}

                log_callback(
                    f"DEBUG: No exact match found for '{search_term}' in {obj_type} search results after iterating all results.")
            else:
                log_callback(f"No results found for '{search_term}' in {obj_type} search.")
        elif response:
            log_callback(
                f"❌ Error during {obj_type} search for '{search_term}': {response.status_code} - {response.text}")

    log_callback(f"❌ Could not find an exact Alation object for: '{name_or_email}'")
    return None