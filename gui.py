# gui.py

import tkinter as tk
from tkinter import messagebox
from ui import main_window, config_window, misc_tools_window

# The unused 'AppState' import has been removed to break the circular dependency.

def start_gui(config, is_token_valid, status_message):
    """
    Initializes and runs the main Tkinter GUI.

    Args:
        config (dict): The application configuration.
        is_token_valid (bool): The initial validity status of the token.
        status_message (str): The initial status message to display.
    """
    try:
        # MainWindow creates its own instance of AppState, so we don't need it here.
        root = main_window.MainWindow(config, is_token_valid, status_message)

        # You can add a menu item or button in the MainWindow class to open the misc tools.
        # For example, inside the MainWindow class in main_window.py, you could have a method:
        #
        # def open_misc_tools(self):
        #     misc_win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        #     misc_win.grab_set()
        #
        # And a button:
        # misc_button = ttk.Button(self, text="Open Misc Tools", command=self.open_misc_tools)
        # misc_button.pack(pady=10)

        root.mainloop()

    except Exception as e:
        # Fallback for critical GUI errors
        messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close: {e}")
        import traceback
        traceback.print_exc()