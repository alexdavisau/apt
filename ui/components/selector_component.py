# ui/components/selector_component.py

import tkinter as tk
from tkinter import ttk
from core.app_state import AppState
from utils import alation_lookup, api_client


class SelectorComponent(ttk.Frame):
    """A reusable component for selecting Hub, Folder, and Template."""

    def __init__(self, parent, app_state: AppState):
        super().__init__(parent, padding=10)
        self.app_state = app_state

        # Data stores for this component
        self.all_documents = []
        self.all_templates = []

        self._create_widgets()

        if self.app_state.is_token_valid:
            self._load_initial_data()

    def _create_widgets(self):
        self.columnconfigure(1, weight=1)

        ttk.Button(self, text="Refresh Alation Data", command=self._load_initial_data).grid(row=0, column=0, padx=5,
                                                                                            pady=5, sticky="w")

        ttk.Label(self, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(self, state="readonly")
        self.hub_selector.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(self, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(self, state="readonly")
        self.folder_selector.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(self, state="readonly")
        self.template_selector.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

    def _load_initial_data(self):
        self.app_state.log_callback("--- Selections: Refreshing data ---")
        self.all_documents = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback,
                                                              force_fetch=True)
        self.all_templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                          force_api_fetch=True)

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Selections: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Selections: No documents found.")

        self.folder_selector.set('')
        self.template_selector.set('')

    def _on_hub_selected(self, event=None):
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        self.app_state.log_callback(f"--- Selections: Populating for Hub ID: {selected_hub_id} ---")

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
            f"✅ Selections: Found {len(folder_display_list) - 1} folders and {len(template_display_names)} compatible templates.")

    def _get_id_from_selection(self, selection_string: str) -> int:
        if not selection_string or "(ID:" not in selection_string: return None
        try:
            id_part = selection_string.split('(ID: ')[-1]
            return int(id_part.replace(')', ''))
        except (ValueError, IndexError):
            return None

    def get_selections(self) -> dict:
        """Returns the selected IDs from the dropdowns."""
        try:
            hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            hub_id = None

        folder_id = self._get_id_from_selection(self.folder_selector.get())
        template_id = self._get_id_from_selection(self.template_selector.get())

        return {
            "hub_id": hub_id,
            "folder_id": folder_id,
            "template_id": template_id
        }