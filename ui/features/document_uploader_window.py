# ui/features/document_uploader_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from core.app_state import AppState
from utils import alation_lookup, api_client


class DocumentUploaderWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Upload Documents")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state

        self.all_documents = []
        self.all_templates = []

        self._create_widgets()

        if self.app_state.is_token_valid:
            self.after(100, self.start_threaded_load)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        uploader_lf = ttk.LabelFrame(main_frame, text="Upload Documents from File", padding=10)
        uploader_lf.grid(row=0, column=0, sticky="nsew")
        uploader_lf.columnconfigure(1, weight=1)

        self.refresh_button = ttk.Button(uploader_lf, text="Refresh Alation Data", command=self.start_threaded_load)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(uploader_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(uploader_lf, state="disabled")
        self.hub_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(uploader_lf, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(uploader_lf, state="disabled")
        self.folder_selector.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(uploader_lf, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(uploader_lf, state="disabled")
        self.template_selector.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.filepath_var = tk.StringVar()
        ttk.Label(uploader_lf, text="File to Upload:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(uploader_lf, textvariable=self.filepath_var, state="readonly").grid(row=4, column=1, padx=5, pady=5,
                                                                                      sticky=tk.EW)
        ttk.Button(uploader_lf, text="Browse...", command=self._select_file).grid(row=4, column=2, padx=5, pady=5)

        self.upload_button = ttk.Button(uploader_lf, text="Upload and Process File", command=self._upload_file,
                                        state="disabled")
        self.upload_button.grid(row=5, column=1, columnspan=2, pady=10)

        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(expand=True, fill="x")

    def start_threaded_load(self):
        """Starts the data loading process in a separate thread."""
        self.hub_selector.set('');
        self.folder_selector.set('');
        self.template_selector.set('')
        self.hub_selector['state'] = 'disabled'
        self.folder_selector['state'] = 'disabled'
        self.template_selector['state'] = 'disabled'
        self.upload_button['state'] = 'disabled'
        self.refresh_button['state'] = 'disabled'

        self.progress_bar.start(10)

        thread = threading.Thread(target=self._load_data_in_background, daemon=True)
        thread.start()

    def _load_data_in_background(self):
        """(Worker Thread) Fetches data from Alation APIs."""
        self.app_state.log_callback("--- Document Uploader: Refreshing all data... ---")

        docs = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback, force_fetch=True)
        templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                 force_api_fetch=True)

        self.after(0, self._update_ui_with_loaded_data, docs, templates)

    def _update_ui_with_loaded_data(self, docs, templates):
        """(Main Thread) Updates the UI with data fetched from the worker thread."""
        self.progress_bar.stop()
        self.all_documents = docs
        self.all_templates = templates

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Document Uploader: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Document Uploader: No documents found.")

        # --- START FIX ---
        # Re-enable all controls now that the data is loaded
        self.hub_selector['state'] = 'readonly'
        self.folder_selector['state'] = 'readonly'
        self.template_selector['state'] = 'readonly'
        self.upload_button['state'] = 'normal'
        self.refresh_button['state'] = 'normal'
        # --- END FIX ---

    def _on_hub_selected(self, event=None):
        # This logic remains the same
        pass

    def _select_file(self):
        # This logic remains the same
        pass

    def _upload_file(self):
        # This logic remains the same
        pass