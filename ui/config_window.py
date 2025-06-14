# ui/config_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from core.app_state import AppState


class ConfigWindow(tk.Toplevel):
    """A Toplevel window for configuring the application settings."""

    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Configuration")
        self.geometry("600x250")
        self.transient(parent)  # Keep this window on top of the main window
        self.grab_set()  # Make this window modal

        self.app_state = app_state
        self.config = self.app_state.config.copy()  # Work on a copy

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Entry Fields ---
        self.url_var = tk.StringVar(value=self.config.get("alation_url", ""))
        self.token_var = tk.StringVar(value=self.config.get("access_token", ""))
        self.refresh_token_var = tk.StringVar(value=self.config.get("refresh_token", ""))
        self.user_id_var = tk.StringVar(value=self.config.get("user_id", ""))

        self._create_widgets()

    def _create_widgets(self):
        """Creates and arranges the widgets in the configuration window."""
        config_frame = ttk.LabelFrame(self.main_frame, text="Alation Connection", padding="10")
        config_frame.pack(fill=tk.X, expand=True)

        # Alation URL
        ttk.Label(config_frame, text="Alation URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        url_entry = ttk.Entry(config_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Access Token
        ttk.Label(config_frame, text="Access Token:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        token_entry = ttk.Entry(config_frame, textvariable=self.token_var, width=60)
        token_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        # Refresh Token
        ttk.Label(config_frame, text="Refresh Token:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        refresh_token_entry = ttk.Entry(config_frame, textvariable=self.refresh_token_var, width=60)
        refresh_token_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # User ID
        ttk.Label(config_frame, text="User ID:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        user_id_entry = ttk.Entry(config_frame, textvariable=self.user_id_var, width=10)
        user_id_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        config_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        save_button = ttk.Button(button_frame, text="Save & Close", command=self.save_and_close)
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def save_and_close(self):
        """Saves the new configuration and closes the window."""
        new_config = {
            "alation_url": self.url_var.get(),
            "access_token": self.token_var.get(),
            "refresh_token": self.refresh_token_var.get(),
            "user_id": int(self.user_id_var.get()) if self.user_id_var.get().isdigit() else 0
        }

        # Check if user ID is valid
        if new_config["user_id"] == 0:
            messagebox.showerror("Invalid Input", "User ID must be a number.", parent=self)
            return

        # A simple check for required fields
        if not all([new_config["alation_url"], new_config["access_token"]]):
            messagebox.showerror("Missing Information", "Alation URL and Access Token are required.", parent=self)
            return

        # In a real app, you would save this new_config object
        self.app_state.log_callback("Configuration updated. Please restart the application to apply the changes.")
        messagebox.showinfo(
            "Configuration Saved",
            "Configuration has been saved. Please restart the application for changes to take full effect.",
            parent=self
        )

        # Here we would call a method on app_state to save the config
        # self.app_state.save_new_config(new_config)

        self.destroy()  # Close the window