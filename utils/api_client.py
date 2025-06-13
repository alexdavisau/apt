import requests
import json
from urllib.parse import urljoin
from config import config_handler
from pathlib import Path
import time

CONFIG_PATH = Path("config.json")

DOCUMENTS_CACHE_PATH = Path("cache/cached_documents.json")
TEMPLATES_CACHE_PATH = Path("cache/cached_templates.json")
CACHE_EXPIRY_SECONDS = 3600  # 1 hour cache expiry. Adjust as needed.


def _load_from_cache(cache_path: Path, log_callback=print) -> tuple[list, bool]:
    """
    Loads data from a JSON cache file.
    Returns: (list of data, boolean indicating if loaded from valid cache)
    """
    if cache_path.exists():
        if time.time() - cache_path.stat().st_mtime < CACHE_EXPIRY_SECONDS:
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                    log_callback(f"✅ Loaded data from cache: {cache_path}")
                    return data, True
            except json.JSONDecodeError as e:
                log_callback(f"❌ Error decoding cache file {cache_path}: {e}. Will fetch from API.")
                cache_path.unlink(missing_ok=True)
                return [], False
        else:
            log_callback(f"⚠️ Cache file {cache_path} is expired. Will fetch from API.")
            cache_path.unlink(missing_ok=True)
            return [], False
    return [], False


def _save_to_cache(cache_path: Path, data: list, log_callback=print) -> None:
    """Saves data to a JSON cache file."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure cache directory exists
    try:
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
        log_callback(f"✅ Data saved to cache: {cache_path}")
    except Exception as e:
        log_callback(f"❌ Error saving data to cache {cache_path}: {e}")


# This helper function is now centralized here to break circular imports.
def _make_api_request_with_retry(method: str, url: str, config: dict, token_refresher: callable, json_data: dict = None,
                                 params: dict = None, timeout: int = 30, log_callback=print):
    """
    Helper function to make an API request with token refresh retry logic.
    Receives the token_refresher function as an argument to break circular dependencies.
    """
    retries = 1

    while retries >= 0:
        headers = {"TOKEN": config["access_token"], "accept": "application/json"}
        if method == "POST":
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)

            if response.status_code in (401, 403) and retries > 0:
                log_callback("⚠️ Access token unauthorized during API call. Attempting to refresh token...")
                success, msg, new_tokens = token_refresher(config, log_callback=log_callback)
                if success:
                    config.update(new_tokens)
                    config_handler.save_config(CONFIG_PATH, config)
                    log_callback("✅ Token refreshed and config updated. Retrying API request...")
                    retries -= 1
                    continue
                else:
                    log_callback(f"❌ Failed to refresh token during API call: {msg}.")
                    return None
            else:
                return response

        except requests.RequestException as e:
            log_callback(f"❌ Request failed during API call: {e}")
            if retries > 0:
                log_callback("Retrying API call due to connection error...")
                retries -= 1
                continue
            return None

    return None


def get_all_documents(config: dict, log_callback=print, force_api_fetch: bool = False) -> list:
    if not force_api_fetch:
        cached_data, from_cache = _load_from_cache(DOCUMENTS_CACHE_PATH, log_callback)
        if from_cache:
            return cached_data

    base_url = config['alation_url'].rstrip('/')
    next_page_url = f"{base_url}/integration/v2/document/?deleted=false&limit=1000"
    all_documents = []
    page_num = 1

    log_callback("Fetching all documents from API...")
    current_url = next_page_url

    from utils.token_checker import refresh_access_token

    while current_url:
        log_callback(f"📄 Fetching page {page_num}...")
        response = _make_api_request_with_retry("GET", current_url, config, token_refresher=refresh_access_token,
                                                log_callback=log_callback,
                                                timeout=60)  # Increased timeout for pagination call

        if response and response.status_code == 200:
            data = response.json()
            all_documents.extend(data)
            next_page_path = response.headers.get('X-Next-Page')

            if next_page_path:
                current_url = urljoin(base_url, next_page_path)
                page_num += 1
            else:
                current_url = None
        elif response:
            log_callback(f"❌ Error fetching documents: {response.status_code} {response.text}")
            break
        else:
            log_callback(f"❌ Failed to fetch documents after retries.")
            break

    if all_documents:
        log_callback(f"✅ Found {len(all_documents)} total documents.")
        _save_to_cache(DOCUMENTS_CACHE_PATH, all_documents, log_callback)
    else:
        log_callback("❌ No documents found from API.")

    return all_documents


def get_all_templates(config: dict, log_callback=print, force_api_fetch: bool = False) -> list:
    if not force_api_fetch:
        cached_data, from_cache = _load_from_cache(TEMPLATES_CACHE_PATH, log_callback)
        if from_cache:
            return cached_data

    url = f"{config['alation_url'].rstrip('/')}/integration/v1/custom_template/"

    log_callback(f"🔍 Fetching master list of all templates from API: {url}...")
    from utils.token_checker import refresh_access_token
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback, timeout=30)

    if response and response.status_code == 200:
        templates = response.json()
        log_callback(f"✅ Found {len(templates)} total templates defined.")
        _save_to_cache(TEMPLATES_CACHE_PATH, templates, log_callback)
        return templates
    elif response:
        log_callback(f"❌ Error fetching templates from API: {response.status_code} {response.text}")
    else:
        log_callback(f"❌ Failed to fetch templates from API after retries.")

    return []