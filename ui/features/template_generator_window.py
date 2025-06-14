# ui/features/template_generator_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from ui.components.selector_component import SelectorComponent
from utils import excel_writer


class TemplateGeneratorWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Generate Excel from Template")
        self.geometry("700x350")
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")

        # Create an instance of the reusable selector component
        self.selectors = SelectorComponent(main_frame, self.app_state)
        self.selectors.pack(expand=True, fill="x", anchor="n")

        # Add the button specific to this feature
        self.create_button = ttk.Button(main_frame, text="Create Excel File", command=self._create_validated_excel)
        self.create_button.pack(pady=20)

    def _create_validated_excel(self):
        selections = self.selectors.get_selections()
        hub_id = selections.get("hub_id")
        folder_id = selections.get("folder_id")
        template_id = selections.get("template_id")

        if not all([hub_id, folder_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub, Folder, and Template first.",
                                   parent=self)
            return

        # CORRECTED LOGIC: Find the visual config object from the list loaded by the selector component
        visual_config_obj = next((vc for vc in self.selectors.visual_configs if vc.get('id') == template_id), None)

        if not visual_config_obj:
            messagebox.showerror("Error",
                                 f"Could not find Visual Config for Template ID {template_id}. This can happen if the Visual Config ID does not match the Template ID.",
                                 parent=self)
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