# ui/features/document_uploader_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from utils import alation_lookup, api_client


class DocumentUploaderWindow(tk.Toplevel):
    """
    A window dedicated to the 'Upload Documents' feature.
    """

    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Document Uploader")
        self.geometry("700x450")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state

        # --- Data Stores for this window ---
        self.all_templates = []
        self.all_documents = []

        self._create_widgets()

        if self.app_state.is_token_valid:
            self._load_initial_data()

    def _create_widgets(self):
        """Creates and arranges widgets for this feature."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(1, weight=1)

        controls_lf = ttk.LabelFrame(main_frame, text="Upload Documents from File", padding=10)
        controls_lf.grid(row=0, column=0, sticky="nsew")
        controls_lf.columnconfigure(1, weight=1)

        ttk.Button(controls_lf, text="Refresh Alation Data", command=self._load_initial_data).grid(row=0, column=0,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky="w")

        ttk.Label(controls_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(controls_lf, state="readonly")
        self.hub_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(controls_lf, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(controls_lf, state="readonly")
        self.folder_selector.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(controls_lf, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(controls_lf, state="readonly")
        self.template_selector.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.filepath_var = tk.StringVar()
        ttk.Label(controls_lf, text="File to Upload:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(controls_lf, textvariable=self.filepath_var, state="readonly").grid(row=4, column=1, padx=5, pady=5,
                                                                                      sticky=tk.EW)
        ttk.Button(controls_lf, text="Browse...", command=self._select_file).grid(row=4, column=2, padx=5, pady=5)

        ttk.Button(controls_lf, text="Upload and Process File", command=self._upload_file).grid(row=5, column=1,
                                                                                                columnspan=2, pady=10)

    def _load_initial_data(self):
        """Loads data from Alation and populates the Hub dropdown."""
        self.app_state.log_callback("--- Document Uploader: Refreshing data ---")
        self.all_documents = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback,
                                                              force_fetch=True)
        self.all_templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                          force_api_fetch=True)

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Document Uploader: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Document Uploader: No documents found.")

        self.folder_selector.set('')
        self.template_selector.set('')

    def _on_hub_selected(self, event=None):
        """Callback when a hub is selected. Populates folders and templates."""
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        self.app_state.log_callback(f"--- Document Uploader: Populating for Hub ID: {selected_hub_id} ---")

        folders = alation_lookup.get_folders_for_hub(self.app_state.config, selected_hub_id,
                                                     self.app_state.log_callback)
        folder_display_list = [f"Hub Root (ID: {selected_hub_id})"]
        folder_display_list.extend([f"{f.get('title')} (ID: {f.get('id')})" for f in folders])
        self.folder_selector['values'] = folder_display_list
        if folder_display_list:
            self.folder_selector.set(folder_display_list[0])

        docs_in_hub = [doc for doc in self.all_documents if doc.get('document_hub_id') == selected_hub_id]
        template_ids_in_hub = {doc.get('template_id') for doc in docs_in_hub if doc.get('template_id')}
        compatible_templates = [t for t in self.all_templates if t.get('id') in template_ids_in_hub]
        template_display_names = sorted([f"{t.get('title')} (ID: {t.get('id')})" for t in compatible_templates])

        self.template_selector['values'] = template_display_names
        if template_display_names:
            self.template_selector.set(template_display_names[0])
        else:
            self.template_selector.set('')

        self.app_state.log_callback(
            f"✅ Document Uploader: Found {len(folder_display_list) - 1} folders and {len(template_display_names)} compatible templates.")

    def _select_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")))
        if filepath:
            self.filepath_var.set(filepath)

    def _upload_file(self):
        messagebox.showinfo("In Progress", "This will eventually trigger the upload process.", parent=self)