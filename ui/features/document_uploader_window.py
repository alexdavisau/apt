# ui/features/document_uploader_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from utils import alation_lookup, api_client


class DocumentUploaderWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Document Uploader")
        self.geometry("700x450")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state

        self.all_documents = []
        self.all_templates = []

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

    def _select_file(self):
        # ... (Same as the previous correct version)
        pass

    def _upload_file(self):
        # ... (Same as the previous correct version)
        pass