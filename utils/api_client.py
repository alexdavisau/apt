import json
import time
from pathlib import Path
from urllib.parse import urljoin

# Import the authentication and request logic from its new, single location
from utils.token_checker import _make_api_request_with_retry, refresh_access_token

DOCUMENTS_CACHE_PATH = Path("cache/cached_documents.json")
TEMPLATES_CACHE_PATH = Path("cache/cached_templates.json")
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

def _load_from_cache(cache_path: Path, log_callback=print) -> tuple[list, bool]:
    """Loads data from a JSON cache file if it's not expired."""
    if cache_path.exists() and time.time() - cache_path.stat().st_mtime < CACHE_EXPIRY_SECONDS:
        try:
            with open(cache_path, "r") as f:
                log_callback(f"✅ Loaded data from cache: {cache_path}")
                return json.load(f), True
        except (json.JSONDecodeError, IOError) as e:
            log_callback(f"❌ Error reading cache file {cache_path}: {e}. Will fetch from API.")
    return [], False

def _save_to_cache(cache_path: Path, data: list, log_callback=print) -> None:
    """Saves data to a JSON cache file."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)
    log_callback(f"✅ Data saved to cache: {cache_path}")

def get_all_documents(config: dict, log_callback=print, force_api_fetch: bool = False) -> list:
    """Fetches all documents from the Alation API, with pagination and caching."""
    if not force_api_fetch:
        cached_data, from_cache = _load_from_cache(DOCUMENTS_CACHE_PATH, log_callback)
        if from_cache:
            return cached_data

    base_url = config['alation_url'].rstrip('/')
    current_url = f"{base_url}/integration/v2/document/?deleted=false&limit=1000"
    all_documents = []
    page_num = 1

    log_callback("Fetching all documents from API...")
    while current_url:
        log_callback(f"📄 Fetching page {page_num}...")
        response = _make_api_request_with_retry("GET", current_url, config, token_refresher=refresh_access_token, log_callback=log_callback, timeout=60)

        if response and response.status_code == 200:
            data = response.json()
            all_documents.extend(data)
            next_page_path = response.headers.get('X-Next-Page')
            current_url = urljoin(base_url, next_page_path) if next_page_path else None
            page_num += 1
        else:
            log_callback(f"❌ Failed to fetch documents. Stopping.")
            break

    if all_documents:
        _save_to_cache(DOCUMENTS_CACHE_PATH, all_documents, log_callback)
    return all_documents

def get_all_templates(config: dict, log_callback=print, force_api_fetch: bool = False) -> list:
    """Fetches all templates from the Alation API, with caching."""
    if not force_api_fetch:
        cached_data, from_cache = _load_from_cache(TEMPLATES_CACHE_PATH, log_callback)
        if from_cache:
            return cached_data

    url = f"{config['alation_url'].rstrip('/')}/integration/v1/custom_template/"
    log_callback(f"🔍 Fetching all templates from API...")
    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token, log_callback=log_callback)

    if response and response.status_code == 200:
        templates = response.json()
        _save_to_cache(TEMPLATES_CACHE_PATH, templates, log_callback)
        return templates

    return []