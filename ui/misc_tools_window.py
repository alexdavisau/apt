# In ui/misc_tools_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

from core.app_state import app_state # CORRECTED: Import lowercase 'app_state'
from utils import alation_lookup
from utils.processing_utils import process_hub_and_folders

logger = logging.getLogger(__name__)

class MiscToolsWindow(tk.Toplevel):
    def __init__(self, parent, app_state: app_state): # CORRECTED: Use lowercase 'app_state' for type hint
        super().__init__(parent)
        self.title("Miscellaneous Tools")
        self.geometry("600x400")
        self.app_state = app_state
        self.config = self.app_state.config
        self.log_callback = self.app_state.log_callback

        self.hubs = []
        self.selected_hub_id = tk.IntVar(value=0)

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_widgets()
        self.load_hubs()

    def _create_widgets(self):
        # Frame for Hub selection
        hub_frame = ttk.LabelFrame(self.main_frame, text="Document Hub Tools", padding="10")
        hub_frame.pack(fill=tk.X, expand=True, pady=5)

        ttk.Label(hub_frame, text="Select Hub:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(hub_frame, state="readonly", width=40)
        self.hub_selector.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self.hub_selected_callback)

        self.process_button = ttk.Button(hub_frame, text="Process Hub", command=self.process_selected_hub)
        self.process_button.grid(row=0, column=2, padx=5, pady=5)
        self.process_button['state'] = 'disabled'

        hub_frame.columnconfigure(1, weight=1)

    def load_hubs(self):
        self.log_callback("Fetching Document Hubs for selection...")
        self.hubs = alation_lookup.get_document_hubs(self.config, log_callback=self.log_callback)
        if self.hubs:
            hub_names = [f"Hub: {hub.get('title', 'Untitled')} (ID: {hub.get('id')})" for hub in self.hubs]
            self.hub_selector['values'] = hub_names
            self.log_callback(f"✅ Found {len(self.hubs)} unique Document Hubs for selection.")
        else:
            self.log_callback("❌ No Document Hubs found or error fetching them.")
            messagebox.showerror("Error", "Could not load any Document Hubs from Alation.")

    def hub_selected_callback(self, event=None):
        selection = self.hub_selector.get()
        if not selection:
            self.selected_hub_id.set(0)
            self.process_button['state'] = 'disabled'
            return

        try:
            # Extract ID from "Hub: Title (ID: 123)"
            hub_id = int(selection.split('(ID:')[-1].replace(')', '').strip())
            self.selected_hub_id.set(hub_id)
            self.process_button['state'] = 'normal'
            self.log_callback(f"▶️ Hub '{selection}' selected. ID: {hub_id}")
        except (ValueError, IndexError):
            self.log_callback(f"❌ Could not parse Hub ID from selection: {selection}")
            self.selected_hub_id.set(0)
            self.process_button['state'] = 'disabled'

    def process_selected_hub(self):
        hub_id = self.selected_hub_id.get()
        if not hub_id:
            messagebox.showwarning("Selection Required", "Please select a Document Hub first.")
            return

        hub_details = alation_lookup.get_hub_details(self.config, hub_id, log_callback=self.log_callback)
        hub_title = hub_details.get('title', f"Hub_{hub_id}")

        output_dir = filedialog.askdirectory(
            title="Select Directory to Save Hub Structure",
            initialdir="."
        )

        if not output_dir:
            self.log_callback("Operation cancelled by user.")
            return

        self.log_callback(f"Starting processing for Hub ID: {hub_id}...")
        self.process_button['state'] = 'disabled'

        try:
            process_hub_and_folders(
                self.config,
                hub_id,
                hub_title,
                output_dir,
                self.log_callback
            )
            messagebox.showinfo("Success", f"Hub structure for '{hub_title}' has been created in:\n{output_dir}")
        except Exception as e:
            logger.error(f"Error processing hub {hub_id}: {e}", exc_info=True)
            messagebox.showerror("Processing Error", f"An error occurred: {e}")
        finally:
            self.process_button['state'] = 'normal'