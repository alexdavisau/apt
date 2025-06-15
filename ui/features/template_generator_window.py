# ui/features/template_generator_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from utils import alation_lookup, excel_writer, visual_config_fetcher


class TemplateGeneratorWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Generate Excel from Template")
        self.geometry("700x400")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state
        self._create_widgets()
        # Start checking for the central data load to complete
        self._wait_for_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        controls_lf = ttk.LabelFrame(main_frame, text="Options", padding=10)
        controls_lf.grid(row=0, column=0, sticky="nsew")
        controls_lf.columnconfigure(1, weight=1)

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

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=5)

    def _wait_for_data(self):
        """Checks if the central AppState has finished loading data."""
        if self.app_state.data_loaded.is_set():
            # Data is ready, stop the progress bar and populate controls
            self.progress_bar.stop()
            self.progress_bar.grid_remove()  # Hide the progress bar
            self._populate_initial_data()
        else:
            # Data is not ready, show progress and check again in 200ms
            self.progress_bar.start(10)
            self.after(200, self._wait_for_data)

    def _populate_initial_data(self):
        """Populates controls with data that has been loaded into AppState."""
        self.app_state.log_callback("--- Template Generator: Populating controls ---")

        if self.app_state.all_documents:
            hub_ids = sorted(list(set(doc['document_hub_id'] for doc in self.app_state.all_documents if
                                      doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.hub_selector['state'] = 'readonly'
            self.app_state.log_callback(f"✅ Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ No document data available in AppState.")

        self.folder_selector.set('')
        self.folder_selector['state'] = 'readonly'
        self.template_selector.set('')
        self.template_selector['state'] = 'readonly'
        self.create_button['state'] = 'normal'

    def _on_hub_selected(self, event=None):
        # ... (This logic is now correct and remains the same)
        pass

    def _create_validated_excel(self):
        # ... (This logic is now correct and remains the same)
        pass