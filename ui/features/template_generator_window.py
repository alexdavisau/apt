# ui/features/template_generator_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from utils import alation_lookup, api_client, excel_writer, visual_config_fetcher


class TemplateGeneratorWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Template Generator")
        self.geometry("700x400")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state

        self.visual_configs = []
        self.all_templates = []
        self.all_documents = []

        self._create_widgets()

        if self.app_state.is_token_valid:
            self._load_initial_data()

    def _create_widgets(self):
        # ... (Same as the previous correct version)
        pass

    def _load_initial_data(self):
        # ... (Same as the previous correct version)
        pass

    def _on_hub_selected(self, event=None):
        # ... (Same as the previous correct version)
        pass

    def _get_id_from_selection(self, selection_string: str) -> int:
        # ... (Same as the previous correct version)
        pass

    def _create_validated_excel(self):
        # ... (Same as the previous correct version)
        pass