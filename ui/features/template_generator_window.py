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

        controls_lf = ttk.LabelFrame(main_frame, text="Options", padding=10)
        controls_lf.pack(fill="x", expand=False)

        self.create_button = ttk.Button(main_frame, text="Create Excel File", command=self._create_validated_excel,
                                        state="disabled")

        self.selectors = SelectorComponent(controls_lf, self.app_state, action_button=self.create_button)
        self.selectors.pack(expand=True, fill="both")

        self.create_button.pack(pady=20)

    def _create_validated_excel(self):
        selections = self.selectors.get_selections()
        hub_id = selections.get("hub_id")
        folder_id = selections.get("folder_id")
        template_id = selections.get("template_id")
        all_templates = selections.get("all_templates")

        if not all([hub_id, folder_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub, Folder, and Template first.",
                                   parent=self)
            return

        template_details = next((t for t in all_templates if t.get('id') == template_id), None)

        if not template_details:
            messagebox.showerror("Error", f"Could not find details for Template ID {template_id}.", parent=self)
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Validated Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"{template_details.get('title', 'template')}_upload.xlsx"
        )
        if not output_path:
            self.app_state.log_callback("Operation cancelled by user.")
            return

        excel_writer.create_template_excel(template_details, hub_id, folder_id, output_path,
                                           self.app_state.log_callback)