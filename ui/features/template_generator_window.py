# ui/features/template_generator_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from core.app_state import AppState
from utils import alation_lookup, api_client, excel_writer, visual_config_fetcher


class TemplateGeneratorWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Generate Excel from Template")
        self.geometry("700x450")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state

        self.all_templates = []
        self.all_documents = []
        self.visual_configs = []

        self._create_widgets()

        if self.app_state.is_token_valid:
            self.after(100, self.start_threaded_load)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        controls_lf = ttk.LabelFrame(main_frame, text="Options", padding=10)
        controls_lf.grid(row=0, column=0, sticky="nsew")
        controls_lf.columnconfigure(1, weight=1)

        self.refresh_button = ttk.Button(controls_lf, text="Refresh Alation Data", command=self.start_threaded_load)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(controls_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(controls_lf, state="disabled")
        self.hub_selector.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(controls_lf, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(controls_lf, state="disabled")
        self.folder_selector.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(controls_lf, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(controls_lf, state="disabled")
        self.template_selector.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        self.create_button = ttk.Button(controls_lf, text="Create Excel File", command=self._create_validated_excel,
                                        state="disabled")
        self.create_button.grid(row=4, column=1, pady=10)

        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(expand=True, fill="x")

    def start_threaded_load(self):
        self.hub_selector.set('');
        self.folder_selector.set('');
        self.template_selector.set('')
        self.hub_selector['state'] = 'disabled'
        self.folder_selector['state'] = 'disabled'
        self.template_selector['state'] = 'disabled'
        self.create_button['state'] = 'disabled'
        self.refresh_button['state'] = 'disabled'

        self.progress_bar.start(10)

        thread = threading.Thread(target=self._load_data_in_background, daemon=True)
        thread.start()

    def _load_data_in_background(self):
        self.app_state.log_callback("--- Template Generator: Refreshing all data... ---")

        docs = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback, force_fetch=True)
        templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                 force_api_fetch=True)
        v_configs = visual_config_fetcher.get_all_visual_configs(self.app_state.config, self.app_state.log_callback)

        self.after(0, self._update_ui_with_loaded_data, docs, templates, v_configs)

    def _update_ui_with_loaded_data(self, docs, templates, v_configs):
        """(Main Thread) Updates the UI with data fetched from the worker thread."""
        self.progress_bar.stop()
        self.all_documents = docs
        self.all_templates = templates
        self.visual_configs = v_configs

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Template Generator: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Template Generator: No documents found.")

        # --- START FIX ---
        # Re-enable all controls now that the data is loaded
        self.hub_selector['state'] = 'readonly'
        self.folder_selector['state'] = 'readonly'
        self.template_selector['state'] = 'readonly'
        self.refresh_button['state'] = 'normal'
        self.create_button['state'] = 'normal'
        # --- END FIX ---

    def _on_hub_selected(self, event=None):
        # This logic remains the same
        pass

    def _create_validated_excel(self):
        # This logic remains the same
        pass