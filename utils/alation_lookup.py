# utils/alation_lookup.py

import logging
from utils.token_checker import _make_api_request_with_retry, refresh_access_token
from utils import api_client  # Import the api_client to use its functions

# Configure logging
logger = logging.getLogger(__name__)


def get_all_documents(config: dict, log_callback=print, force_fetch: bool = False) -> list:
    """Convenience function to fetch all documents via the api_client."""
    log_callback("Fetching all documents for lookup purposes...")
    return api_client.get_all_documents(config, log_callback=log_callback, force_api_fetch=force_fetch)


def get_document_hubs(config: dict, log_callback=print) -> list:
    """
    Fetches all documents from the API and filters them to find Document Hubs.
    Hubs are identified as documents with no parent_folder_id.
    """
    log_callback("Fetching all documents to identify hubs...")
    all_documents = api_client.get_all_documents(config, log_callback=log_callback, force_api_fetch=True)

    if not all_documents:
        log_callback("❌ No documents returned from the API.")
        return []

    # Filter for documents that are hubs (i.e., they have no parent folder)
    hubs = [doc for doc in all_documents if doc.get('parent_folder_id') is None]

    log_callback(f"✅ Found {len(hubs)} Document Hubs.")
    return hubs


def get_folders_for_hub(config: dict, hub_id: int, log_callback=print) -> list:
    """Fetches all folders for a specific Document Hub."""
    log_callback(f"🔍 Fetching folders for Document Hub ID: {hub_id}...")
    url = f"{config['alation_url'].rstrip('/')}/integration/v2/folder/?document_hub_id={hub_id}"

    response = _make_api_request_with_retry(
        "GET",
        url,
        config,
        token_refresher=refresh_access_token,
        log_callback=log_callback
    )

    if response and response.status_code == 200:
        folders = response.json()
        log_callback(f"✅ Found {len(folders)} folders for Document Hub ID {hub_id}.")
        return folders
    elif response:
        log_callback(f"❌ Error fetching folders for Hub ID {hub_id}: {response.status_code} {response.text}")
    else:
        log_callback(f"❌ Failed to fetch folders for Hub ID {hub_id} after retries.")

    return []


def get_hub_details(config: dict, hub_id: int, log_callback=print) -> dict:
    """Fetches detailed information for a specific Document Hub."""
    log_callback(f"🔍 Fetching details for Document Hub ID: {hub_id}...")
    url = f"{config['alation_url'].rstrip('/')}/integration/v2/document_hub/{hub_id}/"

    response = _make_api_request_with_retry(
        "GET",
        url,
        config,
        token_refresher=refresh_access_token,
        log_callback=log_callback
    )

    if response and response.status_code == 200:
        hub_details = response.json()
        log_callback(f"✅ Found details for Hub '{hub_details.get('title', hub_id)}'.")
        return hub_details
    elif response:
        log_callback(f"❌ Error fetching details for Hub ID {hub_id}: {response.status_code} {response.text}")
    else:
        log_callback(f"❌ Failed to fetch details for Hub ID {hub_id} after retries.")

    return {}