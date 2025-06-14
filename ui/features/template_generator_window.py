# ui/features/template_generator_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from ui.components.selector_component import SelectorComponent
from utils import excel_writer, visual_config_fetcher


class TemplateGeneratorWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Generate Excel from Template")
        self.geometry("700x300")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")

        # 1. Create an instance of the reusable selector component
        self.selectors = SelectorComponent(main_frame, self.app_state)
        self.selectors.pack(expand=True, fill="x")

        # 2. Add the button specific to this feature
        ttk.Button(main_frame, text="Create Excel File", command=self._create_validated_excel).pack(pady=10)

    def _create_validated_excel(self):
        selections = self.selectors.get_selections()
        hub_id = selections.get("hub_id")
        folder_id = selections.get("folder_id")
        template_id = selections.get("template_id")

        if not all([hub_id, folder_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub, Folder, and Template first.",
                                   parent=self)
            return

        # Fetching visual_configs is now done inside this function, only when needed.
        visual_configs = visual_config_fetcher.get_all_visual_configs(self.app_state.config,
                                                                      self.app_state.log_callback)
        visual_config_obj = next((vc for vc in visual_configs if vc.get('id') == template_id), None)

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