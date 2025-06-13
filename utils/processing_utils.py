# utils/processing_utils.py

import os
from pathlib import Path
from utils import alation_lookup


def process_hub_and_folders(config: dict, hub_id: int, hub_title: str, base_dir: str, log_callback=print):
    """
    Fetches folders for a hub and creates a corresponding directory structure.

    Args:
        config (dict): The application configuration.
        hub_id (int): The ID of the Document Hub.
        hub_title (str): The title of the Document Hub, used for the root folder name.
        base_dir (str): The base directory where the structure will be created.
        log_callback (callable): A function to handle logging.
    """
    log_callback(f"Processing Hub: '{hub_title}' (ID: {hub_id})")

    # Sanitize the hub title to make it a valid directory name
    safe_hub_title = "".join(c for c in hub_title if c.isalnum() or c in (' ', '_')).rstrip()
    hub_path = Path(base_dir) / safe_hub_title

    try:
        hub_path.mkdir(parents=True, exist_ok=True)
        log_callback(f"✅ Created root directory: {hub_path}")

        # Fetch the folders within the hub
        folders = alation_lookup.get_folders_for_hub(config, hub_id, log_callback=log_callback)

        if not folders:
            log_callback("ℹ️ No sub-folders found within this hub.")
            return

        for folder in folders:
            folder_title = folder.get('title', f"Untitled_Folder_{folder.get('id')}")
            safe_folder_title = "".join(c for c in folder_title if c.isalnum() or c in (' ', '_')).rstrip()
            folder_path = hub_path / safe_folder_title

            folder_path.mkdir(exist_ok=True)
            log_callback(f"  ✅ Created sub-directory: {folder_path}")

    except Exception as e:
        log_callback(f"❌ An error occurred while creating directory structure: {e}")
        raise