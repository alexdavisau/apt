# ui/components/selector_component.py

import tkinter as tk
from tkinter import ttk
import threading
from core.app_state import AppState
from utils import alation_lookup, api_client, visual_config_fetcher


class SelectorComponent(ttk.Frame):
    """A reusable component for selecting Hub, Folder, and Template with threaded data loading."""

    def __init__(self, parent, app_state: AppState):
        super().__init__(parent, padding=10)
        self.app_state = app_state

        # Data stores
        self.all_documents = []
        self.all_templates = []
        self.visual_configs = []

        # To hold references to parent widgets
        self.progress_bar = None
        self.action_button = None

        self._create_widgets()

    def set_progress_bar(self, progress_bar, action_button):
        """Receives the progress bar and action button from the parent window."""
        self.progress_bar = progress_bar
        self.action_button = action_button
        # Now that we have the progress bar, we can start loading data
        if self.app_state.is_token_valid:
            self.after(100, self.start_threaded_load)

    def _create_widgets(self):
        self.columnconfigure(1, weight=1)

        self.refresh_button = ttk.Button(self, text="Refresh Alation Data", command=self.start_threaded_load)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(self, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(self, state="disabled")
        self.hub_selector.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(self, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(self, state="disabled")
        self.folder_selector.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(self, state="disabled")
        self.template_selector.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

    def start_threaded_load(self):
        """Disables controls and starts fetching data in a background thread."""
        self.hub_selector.set('');
        self.folder_selector.set('');
        self.template_selector.set('')
        for widget in [self.hub_selector, self.folder_selector, self.template_selector, self.refresh_button]:
            widget['state'] = 'disabled'
        if self.action_button: self.action_button['state'] = 'disabled'

        if self.progress_bar: self.progress_bar.start(10)

        thread = threading.Thread(target=self._load_data_in_background, daemon=True)
        thread.start()

    def _load_data_in_background(self):
        """(Worker Thread) Fetches all necessary data from Alation APIs."""
        self.app_state.log_callback("--- Selections: Refreshing all data... ---")
        docs = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback, force_fetch=True)
        templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                 force_api_fetch=True)
        v_configs = visual_config_fetcher.get_all_visual_configs(self.app_state.config, self.app_state.log_callback)
        self.after(0, self._update_ui_with_loaded_data, docs, templates, v_configs)

    def _update_ui_with_loaded_data(self, docs, templates, v_configs):
        """(Main Thread) Updates the UI after data has been fetched."""
        if self.progress_bar: self.progress_bar.stop()
        self.all_documents = docs
        self.all_templates = templates
        self.visual_configs = v_configs

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Selections: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Selections: No documents found.")

        for widget in [self.hub_selector, self.folder_selector, self.template_selector, self.refresh_button]:
            widget['state'] = 'readonly'
        if self.action_button: self.action_button['state'] = 'normal'

    def _on_hub_selected(self, event=None):
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        folders = alation_lookup.get_folders_for_hub(self.app_state.config, selected_hub_id,
                                                     self.app_state.log_callback)
        folder_display_list = [f"Hub Root (ID: {selected_hub_id})"]
        folder_display_list.extend([f"{f.get('title')} (ID: {f.get('id')})" for f in folders])
        self.folder_selector['values'] = folder_display_list
        if folder_display_list: self.folder_selector.set(folder_display_list[0])

        template_ids_for_hub = {vc.get('template_id') for vc in self.visual_configs if
                                vc.get('template_id') is not None and str(vc.get('collection_type_id')) == str(
                                    selected_hub_id)}
        compatible_templates = [t for t in self.all_templates if t.get('id') in template_ids_for_hub]
        template_display_names = sorted([f"{t.get('title')} (ID: {t.get('id')})" for t in compatible_templates])

        self.template_selector['values'] = template_display_names
        if template_display_names:
            self.template_selector.set(template_display_names[0])
        else:
            self.template_selector.set('')

    def _get_id_from_selection(self, selection_string: str) -> int:
        if not selection_string or "(ID:" not in selection_string: return None
        try:
            return int(selection_string.split('(ID: ')[-1].replace(')', ''))
        except (ValueError, IndexError):
            return None

    def get_selections(self) -> dict:
        try:
            hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            hub_id = None
        folder_id = self._get_id_from_selection(self.folder_selector.get())
        template_id = self._get_id_from_selection(self.template_selector.get())
        return {"hub_id": hub_id, "folder_id": folder_id, "template_id": template_id}