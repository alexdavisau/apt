# core/app_state.py

import logging
import threading
from utils import alation_lookup, api_client, visual_config_fetcher

logger = logging.getLogger(__name__)


class AppState:
    """A centralized state manager for the application."""

    def __init__(self, log_callback=print):
        self.log_callback = log_callback
        self.config = {}
        self.is_token_valid = False

        # Central data stores
        self.all_documents = []
        self.all_templates = []
        self.visual_configs = []
        self.folders_in_hub = []  # New: to store folders for the selected hub

        self.data_loaded = threading.Event()

    def start_background_load(self):
        """Starts fetching all data from Alation in a background thread."""
        if not self.is_token_valid:
            self.log_callback("Token not valid, skipping data load.")
            return

        self.log_callback("--- Starting background data load... ---")
        thread = threading.Thread(target=self._load_data, daemon=True)
        thread.start()

    def _load_data(self):
        """(Worker Thread) Fetches all data and signals when complete."""
        self.all_documents = alation_lookup.get_all_documents(self.config, self.log_callback, force_fetch=True)
        self.all_templates = api_client.get_all_templates(self.config, self.log_callback, force_api_fetch=True)
        self.visual_configs = visual_config_fetcher.get_all_visual_configs(self.config, self.log_callback)

        self.log_callback("--- Background data load complete. ---")
        self.data_loaded.set()  # Signal that data is ready