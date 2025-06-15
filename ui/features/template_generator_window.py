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
        self._populate_initial_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(1, weight=1)

        controls_lf = ttk.LabelFrame(main_frame, text="Options", padding=10)
        controls_lf.grid(row=0, column=0, sticky="nsew")
        controls_lf.columnconfigure(1, weight=1)

        ttk.Label(controls_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(controls_lf, state="readonly")
        self.hub_selector.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(controls_lf, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_selector = ttk.Combobox(controls_lf, state="readonly")
        self.folder_selector.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.folder_selector.bind("<<ComboboxSelected>>", self._on_folder_selected)

        ttk.Label(controls_lf, text="Template:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(controls_lf, state="readonly")
        self.template_selector.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Button(controls_lf, text="Create Excel File", command=self._create_validated_excel).grid(row=4, column=1,
                                                                                                     pady=10)

    def _populate_initial_data(self):
        """Populates controls with data from the central AppState."""
        self.app_state.log_callback("--- Template Generator: Populating controls ---")

        if self.app_state.all_documents:
            hub_ids = sorted(list(set(doc['document_hub_id'] for doc in self.app_state.all_documents if
                                      doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ No document data available in AppState.")

        self.folder_selector.set('')
        self.template_selector.set('')

    def _on_hub_selected(self, event=None):
        """Populates the Folder dropdown based on the selected Hub."""
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        folders = alation_lookup.get_folders_for_hub(self.app_state.config, selected_hub_id,
                                                     self.app_state.log_callback)
        # The folder data contains the template_id, so we store the full folder object
        self.app_state.folders_in_hub = folders

        folder_display_list = [f"{f.get('title')} (ID: {f.get('id')})" for f in folders]
        self.folder_selector['values'] = folder_display_list
        if folder_display_list:
            self.folder_selector.set(folder_display_list[0])
            self._on_folder_selected()  # Trigger the next step in the cascade
        else:
            self.template_selector['values'] = []
            self.template_selector.set('')

    def _on_folder_selected(self, event=None):
        """Populates the Template dropdown based on the selected Folder."""
        selected_folder_str = self.folder_selector.get()
        folder_id = self._get_id_from_selection(selected_folder_str)

        if folder_id is None: return

        # Find the selected folder object to get its template_id
        selected_folder = next((f for f in self.app_state.folders_in_hub if f.get('id') == folder_id), None)

        if selected_folder and selected_folder.get('template_id'):
            template_id = selected_folder.get('template_id')
            # Find the template's title from the main template list
            template_obj = next((t for t in self.app_state.all_templates if t.get('id') == template_id), None)
            if template_obj:
                display_name = f"{template_obj.get('title')} (ID: {template_id})"
                self.template_selector['values'] = [display_name]
                self.template_selector.set(display_name)
            else:
                self.template_selector.set(f"Unknown Template (ID: {template_id})")
        else:
            self.template_selector['values'] = []
            self.template_selector.set('')

    def _get_id_from_selection(self, selection_string: str) -> int:
        if not selection_string or "(ID:" not in selection_string: return None
        try:
            return int(selection_string.split('(ID: ')[-1].replace(')', ''))
        except (ValueError, IndexError):
            return None

    def _create_validated_excel(self):
        try:
            hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            hub_id = None

        folder_id = self._get_id_from_selection(self.folder_selector.get())
        template_id = self._get_id_from_selection(self.template_selector.get())

        if not all([hub_id, folder_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub, Folder, and Template first.",
                                   parent=self)
            return

        visual_config_obj = next((vc for vc in self.app_state.visual_configs if vc.get('id') == template_id), None)

        if not visual_config_obj:
            messagebox.showerror("Error", f"Could not find Visual Config for Template ID {template_id}.", parent=self)
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Validated Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"template_{template_id}_upload.xlsx"
        )
        if not output_path:
            self.app_state.log_callback("Operation cancelled by user.")
            return

        excel_writer.create_template_excel(visual_config_obj, hub_id, folder_id, output_path,
                                           self.app_state.log_callback)