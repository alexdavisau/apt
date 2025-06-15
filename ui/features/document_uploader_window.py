# ui/features/document_uploader_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.app_state import AppState
from ui.components.selector_component import SelectorComponent


class DocumentUploaderWindow(tk.Toplevel):
    def __init__(self, parent, app_state: AppState):
        super().__init__(parent)
        self.title("Upload Documents")
        self.geometry("700x420")  # Adjusted size
        self.transient(parent)
        self.grab_set()

        self.app_state = app_state
        self.filepath_var = tk.StringVar()
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")

        self.upload_button = ttk.Button(main_frame, text="Upload and Process File", command=self._upload_file,
                                        state="disabled")

        selectors_lf = ttk.LabelFrame(main_frame, text="Selections", padding=10)
        selectors_lf.pack(fill="x", expand=False, pady=5)
        self.selectors = SelectorComponent(selectors_lf, self.app_state, action_button=self.upload_button)
        self.selectors.pack(expand=True, fill="both")

        uploader_lf = ttk.LabelFrame(main_frame, text="File", padding=10)
        uploader_lf.pack(fill="x", expand=False, pady=5)
        uploader_lf.columnconfigure(1, weight=1)

        ttk.Label(uploader_lf, text="File to Upload:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(uploader_lf, textvariable=self.filepath_var, state="readonly").grid(row=0, column=1, padx=5, pady=5,
                                                                                      sticky=tk.EW)
        ttk.Button(uploader_lf, text="Browse...", command=self._select_file).grid(row=0, column=2, padx=5, pady=5)

        self.upload_button.pack(pady=10)

    def _select_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")))
        if filepath:
            self.filepath_var.set(filepath)

    def _upload_file(self):
        selections = self.selectors.get_selections()
        filepath = self.filepath_var.get()

        if not all([selections.get("hub_id"), selections.get("folder_id"), selections.get("template_id"), filepath]):
            messagebox.showwarning("Missing Information", "Please make all selections and choose a file.", parent=self)
            return

        messagebox.showinfo("In Progress", "This will eventually trigger the upload process.", parent=self)