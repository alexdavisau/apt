# gui.py

import tkinter as tk
from tkinter import messagebox
from ui import main_window


def start_gui(config, is_token_valid, status_message):
    """
    Initializes and runs the main Tkinter GUI.
    """
    try:
        # Create an instance of the main window class
        root = main_window.MainWindow(config, is_token_valid, status_message)

        # Start the Tkinter event loop
        root.mainloop()

    except Exception as e:
        # Fallback for critical GUI errors
        messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close: {e}")
        import traceback
        traceback.print_exc()