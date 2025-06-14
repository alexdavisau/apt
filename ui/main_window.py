# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from core.app_state import AppState
from ui import config_window, misc_tools_window
from utils import alation_lookup, api_client


class MainApplication(ttk.Frame):
    """The main application frame that contains all the primary UI elements."""

    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")
        self.parent = parent

        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        self.all_templates = []
        self.all_documents = []

        self._create_menu()
        self._create_layout_and_widgets()
        self._show_frame(self.main_menu_frame)

        self.log_to_console(f"APT Initialized. {status_message}")
        if self.app_state.is_token_valid:
            self._load_initial_data()

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

    def _create_layout_and_widgets(self):
        """Creates and arranges all frames and widgets for the application."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky="new")
        self.main_menu_frame = ttk.Frame(main_container)
        self.uploader_frame = ttk.Frame(main_container)
        self.main_menu_frame.grid(row=0, column=0, sticky="nsew")
        self.uploader_frame.grid(row=0, column=0, sticky="nsew")

        # --- Main Menu Widgets ---
        menu_lf = ttk.LabelFrame(self.main_menu_frame, text="Core Functions", padding=10)
        menu_lf.pack(expand=True, fill="both", padx=5, pady=5)
        ttk.Button(menu_lf, text="Upload Documents", command=lambda: self._show_frame(self.uploader_frame)).pack(
            pady=10, ipadx=10, ipady=5)

        # --- Uploader Widgets ---
        uploader_lf = ttk.LabelFrame(self.uploader_frame, text="Upload Documents from File", padding=10)
        uploader_lf.pack(expand=True, fill="both", padx=5, pady=5)
        uploader_lf.columnconfigure(1, weight=1)

        ttk.Button(uploader_lf, text="< Back to Menu", command=lambda: self._show_frame(self.main_menu_frame)).grid(
            row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Button(uploader_lf, text="Refresh Alation Data", command=self._load_initial_data).grid(row=0, column=0,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky="w")

        ttk.Label(uploader_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(uploader_lf, state="readonly")
        self.hub_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(uploader_lf, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(uploader_lf, state="readonly")
        self.folder_selector.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(uploader_lf, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(uploader_lf, state="readonly")
        self.template_selector.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.filepath_var = tk.StringVar()
        ttk.Label(uploader_lf, text="File to Upload:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(uploader_lf, textvariable=self.filepath_var, state="readonly").grid(row=4, column=1, padx=5, pady=5,
                                                                                      sticky=tk.EW)
        ttk.Button(uploader_lf, text="Browse...", command=self._select_file).grid(row=4, column=2, padx=5, pady=5)

        self.upload_button = ttk.Button(uploader_lf, text="Upload and Process File", command=self._upload_file)
        self.upload_button.grid(row=5, column=1, columnspan=2, pady=10)

        # --- Log Console & Status Bar ---
        log_frame = ttk.LabelFrame(self, text="Log Console", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)
        self.log_console.grid(row=0, column=0, sticky="nsew")

        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.grid(row=2, column=0, sticky="ew")

    def _show_frame(self, frame_to_show):
        frame_to_show.tkraise()

    def _load_initial_data(self):
        """Loads all necessary data from Alation and populates the initial Hub ID dropdown."""
        self.log_to_console("--- Refreshing all data from Alation ---")
        self.all_documents = alation_lookup.get_all_documents(self.app_state.config, self.log_to_console,
                                                              force_fetch=True)
        self.all_templates = api_client.get_all_templates(self.app_state.config, self.log_to_console,
                                                          force_api_fetch=True)

        if self.all_documents:
            # CORRECTED LOGIC: Extract unique document_hub_id values from all documents.
            hub_ids = sorted(list(set(
                doc['document_hub_id']
                for doc in self.all_documents if doc.get('document_hub_id') is not None
            )))
            self.hub_selector['values'] = hub_ids
            self.log_to_console(f"✅ Found {len(hub_ids)} unique Document Hub IDs. Please select one.")
        else:
            self.log_to_console("❌ No documents found, cannot populate Hub IDs.")
            self.hub_selector['values'] = []

        self.folder_selector.set('')
        self.template_selector.set('')

    def _on_hub_selected(self, event=None):
        """Callback when a hub is selected. Populates folders and filtered templates."""
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        self.log_to_console(f"--- Populating folders and templates for Hub ID: {selected_hub_id} ---")

        # --- Populate Folders ---
        folders = alation_lookup.get_folders_for_hub(self.app_state.config, selected_hub_id, self.log_to_console)
        # Add the Hub itself as the root option
        folder_display_list = [f"Hub Root (ID: {selected_hub_id})"]
        folder_display_list.extend([f"{f.get('title')} (ID: {f.get('id')})" for f in folders])
        self.folder_selector['values'] = folder_display_list

        # --- Filter and Populate Templates ---
        docs_in_hub = [doc for doc in self.all_documents if doc.get('document_hub_id') == selected_hub_id]
        template_ids_in_hub = {doc.get('template_id') for doc in docs_in_hub if doc.get('template_id')}

        compatible_templates = [t for t in self.all_templates if t.get('id') in template_ids_in_hub]
        template_titles = [t.get('title') for t in compatible_templates]

        self.template_selector['values'] = sorted(list(set(template_titles)))
        self.log_to_console(f"✅ Found {len(folders)} folders and {len(template_titles)} compatible templates.")

    def _select_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")))
        if filepath:
            self.filepath_var.set(filepath)

    def _upload_file(self):
        messagebox.showinfo("In Progress", "This will eventually trigger the upload process.")

    def open_config_window(self):
        config_win = config_window.ConfigWindow(self, self.app_state)
        config_win.grab_set()

    def open_misc_tools_window(self):
        misc_win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        misc_win.grab_set()

    def log_to_console(self, message):
        self.status_bar.config(text=message)
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)