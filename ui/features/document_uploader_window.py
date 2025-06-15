# ui/features/document_uploader_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from utils import alation_lookup


class DocumentUploaderWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Upload Documents")
        self.geometry("700x450")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state
        self.filepath_var = tk.StringVar()

        self._create_widgets()
        # Start checking for the central data load to complete
        self._wait_for_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        uploader_lf = ttk.LabelFrame(main_frame, text="Upload Documents from File", padding=10)
        uploader_lf.grid(row=0, column=0, sticky="nsew")
        uploader_lf.columnconfigure(1, weight=1)

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

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=5)

    def _wait_for_data(self):
        """Checks if the central AppState has finished loading data."""
        if self.app_state.data_loaded.is_set():
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self._populate_initial_data()
        else:
            self.progress_bar.start(10)
            self.after(200, self._wait_for_data)

    def _populate_initial_data(self):
        """Populates controls with data from AppState."""
        self.app_state.log_callback("--- Document Uploader: Populating controls ---")

        if self.app_state.all_documents:
            hub_ids = sorted(list(set(doc['document_hub_id'] for doc in self.app_state.all_documents if
                                      doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ No document data available in AppState.")

        self.hub_selector['state'] = 'readonly'
        self.folder_selector['state'] = 'readonly'
        self.template_selector['state'] = 'readonly'
        self.upload_button['state'] = 'normal'

    def _on_hub_selected(self, event=None):
        # ... (This logic is now correct and remains the same)
        pass

    def _select_file(self):
        # ... (This logic is unchanged)
        pass

    def _upload_file(self):
        # ... (This logic is unchanged)
        pass