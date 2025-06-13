# ui/config_window.py

import dearpygui.dearpygui as dpg
from pathlib import Path
from config import config_handler
from utils.token_checker import check_token  # Used to check token validity


def create_config_window(config: dict):
    """
    Defines the layout and elements for the configuration window.
    """

    def save_and_recheck_config():
        """Callback to save config and switch back to the main window."""
        config_path = Path("config.json")
        config_handler.save_config_from_gui(config_path)

        # Re-load and re-check the new config
        new_config = config_handler.load_config(config_path)
        is_valid, message = check_token(new_config)

        # Update the status text in the main window
        # Check if status_text exists, as it's in main_window, not config_window
        if dpg.does_item_exist("status_text"):
            dpg.set_value("status_text", message)

        # Switch windows
        dpg.configure_item("config_window", show=False)
        # Ensure main_window exists before showing
        if dpg.does_item_exist("main_window"):
            dpg.configure_item("main_window", show=True)
            dpg.set_primary_window("main_window", True)

    with dpg.window(label="Alation API Configuration", tag="config_window", width=550, height=300,
                    show=False):  # Increased height for user_id
        dpg.add_text("Enter your Alation connection details below.")
        dpg.add_spacer(height=5)

        dpg.add_input_text(label="Alation URL", tag="alation_url", default_value=config.get("alation_url", ""),
                           width=400)
        dpg.add_input_text(label="Access Token", tag="access_token", default_value=config.get("access_token", ""),
                           width=400, password=True)
        dpg.add_input_text(label="Refresh Token", tag="refresh_token", default_value=config.get("refresh_token", ""),
                           width=400)
        dpg.add_input_int(label="User ID", tag="user_id", default_value=config.get("user_id", 0),  # Added User ID
                          width=200, step=1)

        dpg.add_spacer(height=10)
        dpg.add_button(label="Save and Continue", callback=save_and_recheck_config)