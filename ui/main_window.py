# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from core.app_state import AppState
from ui import config_window, misc_tools_window


class MainApplication(ttk.Frame):
    """The main application frame that contains all the primary UI elements."""

    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")

        # parent is the root tk.Tk() window.
        self.parent = parent

        # Initialize the shared application state
        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        # --- 1. Create all widgets first ---
        self._create_menu()

        # Create the status bar (it will be placed at the bottom)
        self.status_bar = ttk.Label(self, text=status_message, relief=tk.SUNKEN, anchor=tk.W, padding="2")

        # Create the log console frame and the text widget inside it
        log_frame = ttk.LabelFrame(self, text="Log Console", padding="5")
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)

        # --- 2. Place all widgets on the screen using the .pack() geometry manager ---

        # Pack the status bar at the bottom first to reserve its space
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        # Pack the log frame to fill all remaining space
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Pack the text widget to fill the log frame
        self.log_console.pack(fill=tk.BOTH, expand=True)

        # --- 3. Log the initial status ---
        self.log_to_console(f"APT Initialized. {status_message}")

    def _create_menu(self):
        """Creates the main menu bar for the application."""
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure", command=self.open_config_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent.quit)

        # Tools Menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Misc Tools", command=self.open_misc_tools_window)

    def open_config_window(self):
        """Opens the configuration window."""
        config_win = config_window.ConfigWindow(self, self.app_state)
        config_win.grab_set()

    def open_misc_tools_window(self):
        """Opens the miscellaneous tools window."""
        misc_win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        misc_win.grab_set()

    def log_to_console(self, message):
        """Appends a message to the log console in a thread-safe way."""
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)