# config.py
import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

def config_exists():
    return CONFIG_PATH.exists()

def load_config():
    if not CONFIG_PATH.exists():
        return None
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(data: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print("Configuration saved.")
