# ui/misc_tools_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

# NOTE: AppState import is removed from here to prevent circular dependency
from utils import alation_lookup
from utils.processing_utils import process_hub_and_folders

logger = logging.getLogger(__name__)

class MiscToolsWindow(tk.Toplevel):
    """
    A Toplevel window for miscellaneous tools, such as creating empty documents
    in a specified hub and folder structure.
    """
    def __init__(self, parent, app_state):
        """
        Initializes the Miscellaneous Tools window.

        Args:
            parent: The parent widget (the main application window).
            app_state: The shared application state object.
        """
        super().__init__(parent)
        self.title("Miscellaneous Tools")
        self.geometry("600x450")

        # --- Defer import to break the circular dependency ---
        from core.app_state import AppState
        if not isinstance(app_state, AppState):
            raise TypeError("app_state must be an instance of AppState")

        self.app_state = app_state
        self.config = self.app_state.config
        self.log_callback = self.app_state.log_callback

        # --- Local State Variables ---
        self.hubs = []
        self.folders = []
        self.selected_hub_id = tk.IntVar(value=0)
        self.selected_folder_id = tk.IntVar(value=0)

        # --- Main Frame ---
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_widgets()
        self.load_hubs()

    def _create_widgets(self):
        """Creates and arranges the widgets in the window."""
        creation_frame = ttk.LabelFrame(self.main_frame, text="Generate Blank Documents", padding="10")
        creation_frame.pack(fill=tk.X, expand=True, pady=5)
        creation_frame.columnconfigure(1, weight=1)

        # Hub Selector
        ttk.Label(creation_frame, text="Select Hub:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(creation_frame, state="readonly", width=40)
        self.hub_selector.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self.hub_selected_callback)

        # Folder Selector
        ttk.Label(creation_frame, text="Select Folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(creation_frame, state="readonly", width=40)
        self.folder_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.folder_selector.bind("<<ComboboxSelected>>", self.folder_selected_callback)

        # Entry for Base Title
        ttk.Label(creation_frame, text="Base Title:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.base_title_entry = ttk.Entry(creation_frame, width=40)
        self.base_title_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.base_title_entry.insert(0, "New Document")

        # Entry for Document Count
        ttk.Label(creation_frame, text="Number to Create:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.doc_count_spinbox = ttk.Spinbox(creation_frame, from_=1, to=100, width=5)
        self.doc_count_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.doc_count_spinbox.set(10)

        # Process Button
        self.process_button = ttk.Button(creation_frame, text="Generate Documents", command=self.generate_documents)
        self.process_button.grid(row=4, column=0, columnspan=3, padx=5, pady=10)
        self.process_button['state'] = 'disabled'

    def load_hubs(self):
        """Loads Document Hubs into the hub selector combobox."""
        self.log_callback("Misc Tools: Fetching Document Hubs...")
        self.hubs = alation_lookup.get_document_hubs(self.config, log_callback=self.log_callback)
        if self.hubs:
            hub_names = [f"{hub.get('title', 'Untitled')} (ID: {hub.get('id')})" for hub in self.hubs]
            self.hub_selector['values'] = hub_names
            self.log_callback(f"✅ Misc Tools: Found {len(self.hubs)} Document Hubs.")
        else:
            self.log_callback("❌ Misc Tools: No Document Hubs found.")
            messagebox.showerror("Error", "Could not load any Document Hubs from Alation.")

    def hub_selected_callback(self, event=None):
        """Handles the selection of a new hub."""
        selection = self.hub_selector.get()
        if not selection:
            return

        hub_id = int(selection.split('(ID:')[-1].replace(')', '').strip())
        self.selected_hub_id.set(hub_id)
        self.log_callback(f"▶️ Misc Tools: Hub '{selection}' selected. ID: {hub_id}")

        self.folder_selector['values'] = []
        self.folder_selector.set('')
        self.process_button['state'] = 'disabled'

        self.log_callback(f"Misc Tools: Fetching folders for Hub ID {hub_id}...")
        self.folders = alation_lookup.get_folders_for_hub(self.config, hub_id, log_callback=self.log_callback)

        folder_names = [f"{folder.get('title', 'Untitled')} (ID: {folder.get('id')})" for folder in self.folders]
        hub_title = selection.split(' (ID:')[0]
        folder_names.insert(0, f"{hub_title} (Hub Root)")

        self.folder_selector['values'] = folder_names
        self.log_callback(f"✅ Misc Tools: Found {len(self.folders)} folders.")

    def folder_selected_callback(self, event=None):
        """Handles the selection of a new folder."""
        selection = self.folder_selector.get()
        if not selection:
            return

        if "(Hub Root)" in selection:
            folder_id = self.selected_hub_id.get() # Use the hub's ID as the parent
        else:
            folder_id = int(selection.split('(ID:')[-1].replace(')', '').strip())

        self.selected_folder_id.set(folder_id)
        self.log_callback(f"▶️ Misc Tools: Folder '{selection}' selected. ID: {folder_id}")
        self.process_button['state'] = 'normal'

    def generate_documents(self):
        """Prepares and initiates the blank document generation process."""
        hub_id = self.selected_hub_id.get()
        folder_id = self.selected_folder_id.get()
        base_title = self.base_title_entry.get()
        count = int(self.doc_count_spinbox.get())

        if not all([hub_id, folder_id, base_title, count > 0]):
            messagebox.showwarning("Missing Information", "Please select a hub, a folder, and provide a valid title and count.")
            return

        self.log_callback(f"🚀 Preparing to create {count} documents titled '{base_title}' in Folder ID {folder_id}...")
        self.process_button['state'] = 'disabled'

        try:
            messagebox.showinfo("Process Started", f"Will now attempt to create {count} documents.\nCheck the application logs for progress.")
            # This is a placeholder for the actual creation logic.
            # In a real scenario, you would call a function like:
            # from utils import upload_manager
            # upload_manager.create_blank_documents(self.config, hub_id, folder_id, base_title, count, self.log_callback)
            self.log_callback("Placeholder: Document creation logic would run here.")

        except Exception as e:
            logger.error(f"Error during document generation setup: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.process_button['state'] = 'normal'