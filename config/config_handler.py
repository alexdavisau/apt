# config/config_handler.py

import json
from pathlib import Path
import dearpygui.dearpygui as dpg # DPG needed for get_value in save_config_from_gui

def load_config(config_path: Path) -> dict:
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    else:
        return {}

def save_config(config_path: Path, config_data: dict) -> None:
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)

def save_config_from_gui(config_path: Path) -> None:
    config_data = {
        "alation_url": dpg.get_value("alation_url"),
        "access_token": dpg.get_value("access_token"),
        "refresh_token": dpg.get_value("refresh_token"),
        "user_id": dpg.get_value("user_id"), # Ensure user_id is saved from GUI
    }
    save_config(config_path, config_data)