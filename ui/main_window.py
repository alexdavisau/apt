# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from core.app_state import AppState
from ui import config_window, misc_tools_window
from utils import alation_lookup, api_client  # Import necessary utils


class MainApplication(ttk.Frame):
    """The main application frame that contains all the primary UI elements."""

    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")

        self.parent = parent

        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        # --- Create Widgets ---
        self._create_menu()
        self._create_main_widgets()  # Encapsulate widget creation

        # --- Initial Data Load ---
        self.log_to_console(f"APT Initialized. {status_message}")
        if self.app_state.is_token_valid:
            self._load_initial_data()

    def _create_menu(self):
        """Creates the main menu bar for the application."""
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

    def _create_main_widgets(self):
        """Creates and arranges the primary widgets for the application."""
        # --- Primary Tools Frame ---
        tools_frame = ttk.LabelFrame(self, text="Primary Tools", padding="10")
        tools_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        tools_frame.columnconfigure(1, weight=1)

        # Hub Selector
        ttk.Label(tools_frame, text="Document Hub:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(tools_frame, state="readonly")
        self.hub_selector.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        # Template Selector
        ttk.Label(tools_frame, text="Template:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(tools_frame, state="readonly")
        self.template_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        # File Selection
        self.filepath_var = tk.StringVar()
        ttk.Label(tools_frame, text="File to Upload:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        file_entry = ttk.Entry(tools_frame, textvariable=self.filepath_var, state="readonly")
        file_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        browse_button = ttk.Button(tools_frame, text="Browse...", command=self._select_file)
        browse_button.grid(row=2, column=2, padx=5, pady=5)

        # Upload Button
        self.upload_button = ttk.Button(tools_frame, text="Upload and Process File", command=self._upload_file,
                                        state="disabled")
        self.upload_button.grid(row=3, column=1, columnspan=2, pady=10)

        # --- Log Console ---
        log_frame = ttk.LabelFrame(self, text="Log Console", padding="5")
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)
        self.log_console.grid(row=0, column=0, sticky="nsew")

        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_initial_data(self):
        """Loads hubs and templates to populate the comboboxes."""
        self.log_to_console("Fetching Document Hubs...")
        hubs = alation_lookup.get_document_hubs(self.app_state.config, log_callback=self.log_to_console)
        if hubs:
            hub_names = [f"{hub.get('title', 'Untitled')} (ID: {hub.get('id')})" for hub in hubs]
            self.hub_selector['values'] = hub_names

        self.log_to_console("Fetching Templates...")
        templates = api_client.get_all_templates(self.app_state.config, log_callback=self.log_to_console)
        if templates:
            template_names = [t.get('title', 'Untitled') for t in templates]
            self.template_selector['values'] = template_names

        self.upload_button['state'] = 'normal'

    def _select_file(self):
        """Opens a file dialog to select a file."""
        filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filepath:
            self.filepath_var.set(filepath)
            self.log_to_console(f"Selected file: {filepath}")

    def _upload_file(self):
        """Placeholder for the upload functionality."""
        hub = self.hub_selector.get()
        template = self.template_selector.get()
        filepath = self.filepath_var.get()

        if not all([hub, template, filepath]):
            messagebox.showwarning("Missing Information", "Please select a Hub, a Template, and a File to upload.")
            return

        self.log_to_console("--- Starting Upload Process ---")
        self.log_to_console(f"Hub: {hub}")
        self.log_to_console(f"Template: {template}")
        self.log_to_console(f"File: {filepath}")
        self.log_to_console("NOTE: Actual upload logic is not yet implemented.")
        messagebox.showinfo("In Progress", "This will eventually trigger the upload process.")

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
        self.status_bar.config(text=message)
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)