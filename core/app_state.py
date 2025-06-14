# core/app_state.py

import logging
from config import config_handler

# Configure logging
logger = logging.getLogger(__name__)

class AppState:
    """A centralized state manager for the application."""
    def __init__(self, log_callback=print):
        self.log_callback = log_callback
        self.config = {}
        self.is_configured = False
        self.is_token_valid = False

    def check_initial_config(self):
        """
        Checks if the initial configuration is valid based on loaded data.
        Note: This does not validate the token, which is now handled at startup.
        """
        if self.config.get('alation_url') and self.config.get('access_token'):
            self.is_configured = True
        else:
            self.is_configured = False
            self.log_callback("⚠️ Config not found or incomplete. Please configure.")

    def save_new_config(self, new_config: dict):
        """Saves a new configuration and updates the state."""
        self.config = new_config
        # The config_path needs to be managed appropriately, assuming a default path here
        config_handler.save_config(config_handler.CONFIG_PATH, self.config)
        self.log_callback("✅ Configuration saved.")
        self.check_initial_config() # Re-check the config state
        # Token validation will need to be re-triggered from the UI/main logic after this.