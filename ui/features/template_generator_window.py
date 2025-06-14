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
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(1, weight=1)

        controls_lf = ttk.LabelFrame(main_frame, text="Create Validated Excel Template", padding=10)
        controls_lf.grid(row=0, column=0, sticky="nsew")
        controls_lf.columnconfigure(1, weight=1)

        ttk.Button(controls_lf, text="Refresh Alation Data", command=self._load_initial_data).grid(row=0, column=0,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky="w")

        ttk.Label(controls_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.hub_selector = ttk.Combobox(controls_lf, state="readonly")
        self.hub_selector.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(controls_lf, text="Template:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_selector = ttk.Combobox(controls_lf, state="readonly")
        self.template_selector.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Button(controls_lf, text="Create Excel File", command=self._create_validated_excel).grid(row=3, column=1,
                                                                                                     pady=10)

    def _load_initial_data(self):
        self.app_state.log_callback("--- Template Generator: Refreshing data ---")
        self.all_documents = alation_lookup.get_all_documents(self.app_state.config, self.app_state.log_callback,
                                                              force_fetch=True)
        self.all_templates = api_client.get_all_templates(self.app_state.config, self.app_state.log_callback,
                                                          force_api_fetch=True)
        self.visual_configs = visual_config_fetcher.get_all_visual_configs(self.app_state.config,
                                                                           self.app_state.log_callback)

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.hub_selector['values'] = hub_ids
            self.app_state.log_callback(f"✅ Template Generator: Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.app_state.log_callback("❌ Template Generator: No documents found.")

        self.template_selector.set('')

    def _on_hub_selected(self, event=None):
        try:
            selected_hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            return

        self.app_state.log_callback(f"--- Template Generator: Populating for Hub ID: {selected_hub_id} ---")

        template_ids_for_hub = {vc['template_id'] for vc in self.visual_configs if
                                str(vc.get('collection_type_id')) == str(selected_hub_id)}
        compatible_templates = [t for t in self.all_templates if t.get('id') in template_ids_for_hub]
        template_display_names = sorted([f"{t.get('title')} (ID: {t.get('id')})" for t in compatible_templates])

        self.template_selector['values'] = template_display_names
        if template_display_names:
            self.template_selector.set(template_display_names[0])
        else:
            self.template_selector.set('')

        self.app_state.log_callback(f"✅ Template Generator: Found {len(template_display_names)} compatible templates.")

    def _get_id_from_selection(self, selection_string: str) -> int:
        if not selection_string or "(ID:" not in selection_string:
            return None
        try:
            return int(selection_string.split('(ID: ')[-1].replace(')', ''))
        except (ValueError, IndexError):
            return None

    def _create_validated_excel(self):
        try:
            hub_id = int(self.hub_selector.get())
        except (ValueError, TypeError):
            hub_id = None

        template_id = self._get_id_from_selection(self.template_selector.get())

        if not all([hub_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub and Template first.", parent=self)
            return

        visual_config_obj = next((vc for vc in self.visual_configs if vc.get('template_id') == template_id), None)

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

        excel_writer.create_template_excel(visual_config_obj, hub_id, hub_id, output_path, self.app_state.log_callback)