# core/app_state.py

# Global variables to hold application state
all_documents = [] # All documents fetched from Alation
all_available_templates = [] # All templates fetched from Alation

# Currently selected items (IDs and details) for the main window
selected_hub_id = None
selected_folder_id = None
selected_template_id = None
selected_template_details = None # Full details for the selected template

# Data for dropdowns (derived from all_documents/all_available_templates)
# These lists are populated by UI functions in main_window and misc_tools_window.
hub_names_for_combo = []
folder_titles_for_combo = []
template_titles_for_combo = []

# Functions to update the state
def set_all_documents(docs: list):
    global all_documents
    all_documents = docs

def set_all_available_templates(templates: list):
    global all_available_templates
    all_available_templates = templates

def set_selected_hub(hub_id: int, hub_name: str):
    global selected_hub_id
    selected_hub_id = hub_id

def set_selected_folder(folder_id: int, folder_name: str):
    global selected_folder_id
    selected_folder_id = folder_id

def set_selected_template(template_id: int, template_details: dict):
    global selected_template_id, selected_template_details
    selected_template_id = template_id
    selected_template_details = template_details

def clear_selections():
    global selected_hub_id, selected_folder_id, selected_template_id, selected_template_details
    selected_hub_id = None
    selected_folder_id = None
    selected_template_id = None
    selected_template_details = None