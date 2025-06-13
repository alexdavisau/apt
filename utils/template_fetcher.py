import requests  # This import is now redundant as requests is used via _make_api_request_with_retry
import time
from urllib.parse import urljoin

from utils.api_client import _make_api_request_with_retry
from utils.token_checker import refresh_access_token


def get_document_ids(config: dict, log_callback=print) -> list:
    base_url = config['alation_url'].rstrip('/')
    url = f"{base_url}/integration/v2/document/?deleted=false&limit=500&skip=0"

    log_callback(f"➡️ Step 1: Fetching Document IDs from {url}...")

    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback)

    if response and response.status_code == 200:
        docs = response.json()
        ids = [doc['id'] for doc in docs]
        log_callback(f"✅ Found {len(ids)} Document IDs.")
        return ids
    elif response:
        log_callback(f"❌ Error fetching Document IDs: {response.status_code} {response.text}")
        return []
    else:
        log_callback(f"❌ Failed to fetch Document IDs after retries.")
        return []


def get_document_details(config: dict, doc_id: int, log_callback=print) -> dict:
    url = f"{config['alation_url'].rstrip('/')}/integration/v2/document/{doc_id}/"

    try:
        time.sleep(0.05)
        response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                                log_callback=log_callback)

        if response and response.status_code == 200:
            return response.json()
        elif response:
            log_callback(f"❌ Error fetching details for doc {doc_id}: {response.status_code} {response.text}")
            return None
        else:
            log_callback(f"❌ Failed to fetch details for doc {doc_id} after retries.")
            return None
    except Exception as e:
        log_callback(f"❌ An unexpected error occurred while fetching document details for {doc_id}: {e}")
        return None


def get_folders_for_hub(config: dict, document_hub_id: int, log_callback=print) -> list:
    base_url = config['alation_url'].rstrip('/')
    url = f"{base_url}/integration/v2/folder/?document_hub_id={document_hub_id}"

    log_callback(f"🔍 Fetching folders for Document Hub ID: {document_hub_id} from {url}...")

    response = _make_api_request_with_retry("GET", url, config, token_refresher=refresh_access_token,
                                            log_callback=log_callback)

    if response and response.status_code == 200:
        folders = response.json()
        log_callback(f"✅ Found {len(folders)} folders for Document Hub ID {document_hub_id}.")
        return folders
    elif response:
        log_callback(
            f"❌ Error fetching folders for Document Hub ID {document_hub_id}: {response.status_code} {response.text}")
        return []
    else:
        log_callback(f"❌ Failed to fetch folders for Document Hub ID {document_hub_id} after retries.")
        return []