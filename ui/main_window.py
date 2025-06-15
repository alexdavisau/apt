# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from core.app_state import AppState
from ui import config_window, misc_tools_window
from ui.features import template_generator_window, document_uploader_window


class MainApplication(ttk.Frame):
    """The main application frame that acts as a menu to launch tools."""

    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")
        self.parent = parent

        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        self._create_menu()
        self._create_widgets()

        self.log_to_console(f"APT Initialized. {status_message}")
        # Start loading data in the background as soon as the app starts
        self.app_state.start_background_load()

    def _create_menu(self):
        # ... (This method is unchanged)
        pass

    def _create_widgets(self):
        # ... (This method is unchanged)
        pass

    def _open_feature_window(self, WindowClass):
        """Generic function to open a feature window."""
        if not self.app_state.is_token_valid:
            messagebox.showerror("Error", "Token is not valid. Please configure first.")
            return
        # CORRECTED: Simply open the window and let it handle its own state.
        win = WindowClass(self, self.app_state)
        win.grab_set()

    def open_template_generator(self):
        self._open_feature_window(template_generator_window.TemplateGeneratorWindow)

    def open_document_uploader(self):
        self._open_feature_window(document_uploader_window.DocumentUploaderWindow)

    # ... (Other methods unchanged)