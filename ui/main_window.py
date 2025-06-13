# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
# The AppState import is removed from the top of the file
from ui import config_window, misc_tools_window


class MainWindow(tk.Tk):
    """The main application window for the Alation Power Tools."""

    def __init__(self, config, is_token_valid, status_message):
        super().__init__()
        self.title("APT - Alation Power Tools")
        self.geometry("800x600")

        # --- Defer import to break the circular dependency ---
        from core.app_state import AppState

        # Initialize the shared application state
        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        # --- Menu Bar ---
        self._create_menu()

        # --- Main Content Frame ---
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # --- Log Console ---
        log_frame = ttk.LabelFrame(self.main_frame, text="Log Console", padding="5")
        log_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)
        self.log_console.grid(row=0, column=0, sticky="nsew")

        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text=status_message, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Log the initial status
        self.log_to_console(f"APT Initialized. {status_message}")

    def _create_menu(self):
        """Creates the main menu bar for the application."""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure", command=self.open_config_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Tools Menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Misc Tools", command=self.open_misc_tools_window)

    def open_config_window(self):
        """Opens the configuration window."""
        config_win = config_window.ConfigWindow(self, self.app_state)
        config_win.grab_set()  # Make the window modal to the main window

    def open_misc_tools_window(self):
        """Opens the miscellaneous tools window."""
        misc_win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        misc_win.grab_set()

    def log_to_console(self, message):
        """Appends a message to the log console in a thread-safe way."""
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)  # Scroll to the bottom
        self.update_idletasks()  # Refresh the UI