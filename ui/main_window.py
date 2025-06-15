# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from core.app_state import AppState
from ui import config_window, misc_tools_window
# Import our feature windows
from ui.features import template_generator_window
from ui.features import document_uploader_window


class MainApplication(ttk.Frame):
    """The main application frame that acts as a menu to launch tools."""

    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")
        self.parent = parent

        # The AppState is passed the log_to_console method, which must exist
        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        self._create_menu()
        self._create_widgets()

        self.log_to_console(f"APT Initialized. {status_message}")

    def _create_menu(self):
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure", command=self.open_config_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent.quit)
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Misc Tools", command=self.open_misc_tools_window)

    def _create_widgets(self):
        """Creates the main menu buttons and the log console."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_menu_frame = ttk.LabelFrame(self, text="Core Functions", padding=10)
        main_menu_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        ttk.Button(main_menu_frame, text="Generate Excel from Template", command=self.open_template_generator).pack(
            pady=10, ipadx=10, ipady=5)
        ttk.Button(main_menu_frame, text="Upload Documents", command=self.open_document_uploader).pack(pady=10,
                                                                                                       ipadx=10,
                                                                                                       ipady=5)

        log_frame = ttk.LabelFrame(self, text="Log Console", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)
        self.log_console.grid(row=0, column=0, sticky="nsew")

        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def _open_feature_window(self, WindowClass):
        """Generic function to open a feature window."""
        if not self.app_state.is_token_valid:
            messagebox.showerror("Error", "Token is not valid. Please configure first.")
            return
        win = WindowClass(self, self.app_state)
        win.grab_set()

    def open_template_generator(self):
        """Opens the Template Generator feature window."""
        self._open_feature_window(template_generator_window.TemplateGeneratorWindow)

    def open_document_uploader(self):
        """Opens the Document Uploader feature window."""
        self._open_feature_window(document_uploader_window.DocumentUploaderWindow)

    def open_config_window(self):
        win = config_window.ConfigWindow(self, self.app_state)
        win.grab_set()

    def open_misc_tools_window(self):
        win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        win.grab_set()

    # --- START FIX ---
    # This method was missing after the refactor.
    def log_to_console(self, message):
        """Appends a message to the log console in a thread-safe way."""
        self.status_bar.config(text=message)
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)
    # --- END FIX ---