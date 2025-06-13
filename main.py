import platform
from pathlib import Path
from config.config_handler import load_config
from utils.token_checker import check_token
import gui


def main():
    """
    Initializes the application, checks the token, and starts the GUI.
    """
    print(f"Running Python version: {platform.python_version()} ({platform.python_implementation()})")

    config_path = Path("config.json")
    config = load_config(config_path)

    # Check if the token is valid before starting the GUI
    is_token_valid, status_message = check_token(config)

    # Print the final token status to the console
    print(status_message)

    # Start the GUI and pass the initial state
    gui.start_gui(config, is_token_valid, status_message)


if __name__ == "__main__":
    main()