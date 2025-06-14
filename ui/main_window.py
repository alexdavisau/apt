# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from core.app_state import AppState
from ui import config_window, misc_tools_window
from utils import alation_lookup, api_client, excel_writer, visual_config_fetcher


class MainApplication(ttk.Frame):
    def __init__(self, parent, config, is_token_valid, status_message):
        super().__init__(parent, padding="10")
        self.parent = parent

        self.app_state = AppState(log_callback=self.log_to_console)
        self.app_state.config = config
        self.app_state.is_token_valid = is_token_valid

        self.visual_configs = []
        self.all_documents = []

        self._create_menu()
        self._create_layout_and_widgets()
        self._show_frame(self.main_menu_frame)

        self.log_to_console(f"APT Initialized. {status_message}")
        if self.app_state.is_token_valid:
            self._load_initial_data()

    def _create_menu(self):
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure", command=self.open_config_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent.quit)
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Misc Tools", command=self.open_misc_tools_window)

    def _create_layout_and_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky="new")
        self.main_menu_frame = ttk.Frame(main_container)
        self.uploader_frame = ttk.Frame(main_container)
        self.excel_creator_frame = ttk.Frame(main_container)

        self.main_menu_frame.grid(row=0, column=0, sticky="nsew")
        self.uploader_frame.grid(row=0, column=0, sticky="nsew")
        self.excel_creator_frame.grid(row=0, column=0, sticky="nsew")

        self._create_main_menu_widgets()
        self._create_excel_creator_widgets()
        self._create_common_widgets()

    def _show_frame(self, frame_to_show):
        frame_to_show.tkraise()

    def _create_main_menu_widgets(self):
        menu_lf = ttk.LabelFrame(self.main_menu_frame, text="Core Functions", padding=10)
        menu_lf.pack(expand=True, fill="both", padx=5, pady=5)
        # Simplified to one primary function for now
        ttk.Button(menu_lf, text="Create Excel Template",
                   command=lambda: self._show_frame(self.excel_creator_frame)).pack(pady=10, ipadx=10, ipady=5)

    def _create_excel_creator_widgets(self):
        excel_lf = ttk.LabelFrame(self.excel_creator_frame, text="Create Validated Excel Template", padding=10)
        excel_lf.pack(expand=True, fill="both", padx=5, pady=5)
        excel_lf.columnconfigure(1, weight=1)

        ttk.Button(excel_lf, text="< Back to Menu", command=lambda: self._show_frame(self.main_menu_frame)).grid(row=0,
                                                                                                                 column=2,
                                                                                                                 padx=5,
                                                                                                                 pady=5,
                                                                                                                 sticky="e")
        ttk.Button(excel_lf, text="Refresh Alation Data", command=self._load_initial_data).grid(row=0, column=0, padx=5,
                                                                                                pady=5, sticky="w")

        ttk.Label(excel_lf, text="Document Hub ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.excel_hub_selector = ttk.Combobox(excel_lf, state="readonly")
        self.excel_hub_selector.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.excel_hub_selector.bind("<<ComboboxSelected>>", self._on_hub_selected)

        ttk.Label(excel_lf, text="Template:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.excel_template_selector = ttk.Combobox(excel_lf, state="readonly")
        self.excel_template_selector.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Button(excel_lf, text="Create Excel File", command=self._create_validated_excel).grid(row=3, column=1,
                                                                                                  columnspan=2, pady=10)

    def _create_common_widgets(self):
        log_frame = ttk.LabelFrame(self, text="Log Console", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', wrap=tk.WORD, height=10)
        self.log_console.grid(row=0, column=0, sticky="nsew")

        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.grid(row=2, column=0, sticky="ew")

    def _load_initial_data(self):
        self.log_to_console("--- Refreshing all data from Alation ---")
        self.all_documents = alation_lookup.get_all_documents(self.app_state.config, self.log_to_console,
                                                              force_fetch=True)
        self.visual_configs = visual_config_fetcher.get_all_visual_configs(self.app_state.config, self.log_to_console)

        if self.all_documents:
            hub_ids = sorted(list(
                set(doc['document_hub_id'] for doc in self.all_documents if doc.get('document_hub_id') is not None)))
            self.excel_hub_selector['values'] = hub_ids
            self.log_to_console(f"✅ Found {len(hub_ids)} unique Document Hub IDs.")
        else:
            self.log_to_console("❌ No documents found.")

        self.excel_template_selector.set('')

    def _on_hub_selected(self, event=None):
        try:
            selected_hub_id = int(self.excel_hub_selector.get())
        except (ValueError, TypeError):
            return

        self.log_to_console(f"--- Populating templates for Hub ID: {selected_hub_id} ---")

        # Find templates associated with this hub from the visual config data
        # Note: This logic assumes 'id' in visual_config corresponds to a Hub ID.
        # This might need adjustment based on the actual visual_config structure.
        compatible_templates = [
            vc for vc in self.visual_configs
            if vc.get('layout_otype') == 'glossary_term'  # As per docs, this implies it's a template for a hub
        ]

        template_display_names = sorted([f"{t.get('title')} (ID: {t.get('id')})" for t in compatible_templates])

        self.excel_template_selector['values'] = template_display_names
        if template_display_names:
            self.excel_template_selector.set(template_display_names[0])

        self.log_to_console(f"✅ Found {len(template_display_names)} compatible templates.")

    def _get_id_from_selection(self, selection_string: str) -> int:
        if not selection_string or "(ID:" not in selection_string: return None
        try:
            return int(selection_string.split('(ID: ')[-1].replace(')', ''))
        except (ValueError, IndexError):
            return None

    def _create_validated_excel(self):
        try:
            hub_id = int(self.excel_hub_selector.get())
        except (ValueError, TypeError):
            hub_id = None

        # The folder ID is not part of this simplified workflow
        folder_id = hub_id

        template_id = self._get_id_from_selection(self.excel_template_selector.get())

        if not all([hub_id, template_id]):
            messagebox.showwarning("Selection Required", "Please select a Hub and Template first.", parent=self)
            return

        # Find the visual config object that corresponds to our selected template
        visual_config_obj = next((vc for vc in self.visual_configs if vc.get('id') == template_id), None)

        if not visual_config_obj:
            messagebox.showerror("Error", f"Could not find Visual Config for Template ID {template_id}.", parent=self)
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Validated Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"{visual_config_obj.get('title', 'template')}_upload.xlsx"
        )

        if not output_path:
            self.log_to_console("Operation cancelled by user.")
            return

        excel_writer.create_template_excel(visual_config_obj, hub_id, folder_id, output_path, self.log_to_console)

    def open_config_window(self):
        config_win = config_window.ConfigWindow(self, self.app_state)
        config_win.grab_set()

    def open_misc_tools_window(self):
        misc_win = misc_tools_window.MiscToolsWindow(self, self.app_state)
        misc_win.grab_set()

    def log_to_console(self, message):
        self.status_bar.config(text=message)
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)