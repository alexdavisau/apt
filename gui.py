import dearpygui.dearpygui as dpg
from core import constants
from ui import main_window, config_window, misc_tools_window  # Import misc_tools_window


def create_log_window(y_pos: int):
    """Creates the log window at the bottom of the application, initially collapsed."""
    with dpg.window(label="Log Output", tag="log_window", pos=(0, y_pos), width=700, height=200, collapsed=True):
        dpg.add_text("Application log will appear here...", tag="log_text", wrap=680)


def start_gui(config: dict, is_token_valid: bool, status_message: str):
    """
    Creates the Dear PyGui context and manages the main application loop.
    """
    dpg.create_context()
    dpg.create_viewport(title=constants.APP_TITLE, width=700, height=620)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    viewport_height = dpg.get_viewport_height()
    collapsed_height_estimate = 25
    log_window_y_pos = viewport_height - collapsed_height_estimate

    # Create all application windows
    config_window.create_config_window(config)
    main_window.create_main_window(config, status_message)
    create_log_window(log_window_y_pos)

    # Create misc_tools_window once on startup, keep it hidden initially
    misc_tools_window.create_misc_tools_window(
        config=config,
        log_callback=main_window.log_message,  # Pass main_window's module-level log_message
        fetch_hubs_callback=main_window.fetch_hubs_callback  # Pass main_window's module-level fetch_hubs_callback
    )
    dpg.configure_item("misc_tools_window", show=False)

    if is_token_valid:
        dpg.configure_item("main_window", show=True)
        dpg.set_primary_window("main_window", True)
    else:
        dpg.configure_item("config_window", show=True)
        dpg.set_primary_window("config_window", True)

    dpg.start_dearpygui()
    dpg.destroy_context()