# ui/misc_tools_window.py

import dearpygui.dearpygui as dpg
from core import app_state
from utils import upload_manager, api_client, template_fetcher
import json

# --- Module-level Global Variables for Misc Tools Window's Context ---
# These will be set once by create_misc_tools_window and then accessed by all module-level callbacks.
_config = None
_log_callback = None
_fetch_hubs_callback = None

# Local state for selections within misc_tools_window (also module-level)
_selected_hub_id_misc = None
_selected_folder_id_misc = None
_selected_template_id_misc = None
_selected_template_details_misc = None


# --- Module-level Callbacks for Misc Tools Window ---

# This function is now at the module level
def refresh_misc_data_and_combos(sender, app_data):  # DPG callbacks always receive sender, app_data
    """
    Populates the Hub, Folder, and Template combos in the misc tools window.
    Called when the window is opened or data needs refreshing.
    """
    global _selected_hub_id_misc, _selected_folder_id_misc, _selected_template_id_misc, _selected_template_details_misc

    if _config is None:
        _log_callback("❌ Misc Tools: Configuration not loaded. Please fetch data in main window first.")
        return

    if not app_state.all_documents or not app_state.all_available_templates:
        _log_callback(
            "⚠️ Misc Tools: Main data not loaded. Please ensure 'Fetch Document Hubs & Templates' is clicked in Main Window.")
        dpg.configure_item("misc_hub_combo", items=[], enabled=False)
        dpg.configure_item("misc_folder_combo", items=[], enabled=False)
        dpg.configure_item("misc_template_combo", items=[], enabled=False)
        dpg.configure_item("create_empty_button", enabled=False)
        return

    hub_display_names = []
    for h_id in app_state.hub_names_for_combo:
        hub_doc = next(
            (doc for doc in app_state.all_documents if doc.get('id') == h_id and doc.get('parent_folder_id') is None),
            None)
        if hub_doc and hub_doc.get('title'):
            hub_display_names.append(f"{hub_doc['title']} (ID: {h_id})")
        else:
            hub_display_names.append(f"Hub ID: {h_id}")

    if hub_display_names:
        dpg.configure_item("misc_hub_combo", items=hub_display_names, enabled=True)
        _log_callback(f"✅ Misc Tools: Found {len(hub_display_names)} unique Document Hubs for selection.")
        # Auto-select the main window's current hub if available and valid in this list
        if app_state.selected_hub_id and f"Hub ID: {app_state.selected_hub_id}" in hub_display_names:
            dpg.set_value("misc_hub_combo", f"Hub ID: {app_state.selected_hub_id}")
            hub_selected_callback_misc_internal(None, None)
        elif app_state.selected_hub_id and any(
                f" (ID: {app_state.selected_hub_id})" in name for name in hub_display_names):
            matching_display_name = next(
                (name for name in hub_display_names if f" (ID: {app_state.selected_hub_id})" in name), None)
            if matching_display_name:
                dpg.set_value("misc_hub_combo", matching_display_name)
                hub_selected_callback_misc_internal(None, None)
        else:
            _log_callback("No main window hub pre-selected or found in misc tools list.")
            dpg.configure_item("misc_folder_combo", items=[], enabled=False)
            dpg.configure_item("misc_template_combo", items=[], enabled=False)
            dpg.configure_item("create_empty_button", enabled=False)
            _selected_hub_id_misc = None
            _selected_folder_id_misc = None
            _selected_template_id_misc = None
            _selected_template_details_misc = None

    else:
        dpg.configure_item("misc_hub_combo", items=[], enabled=False)
        dpg.configure_item("misc_folder_combo", items=[], enabled=False)
        dpg.configure_item("misc_template_combo", items=[], enabled=False)
        dpg.configure_item("create_empty_button", enabled=False)
        _log_callback("❌ Misc Tools: No Document Hubs found in loaded data.")


# This function is now at the module level
def hub_selected_callback_misc_internal(sender, app_data):
    global _selected_hub_id_misc, _selected_folder_id_misc, _selected_template_id_misc, _selected_template_details_misc

    selected_hub_value = dpg.get_value("misc_hub_combo")
    if not selected_hub_value: return

    if " (ID: " in selected_hub_value:
        hub_id_str = selected_hub_value.split(" (ID: ")[1].rstrip(")")
    else:
        hub_id_str = selected_hub_value.replace("Hub ID: ", "")

    _selected_hub_id_misc = int(hub_id_str)

    _log_callback(f"\n▶️ Misc Tools: Hub '{selected_hub_value}' selected. ID: {_selected_hub_id_misc}")

    dpg.configure_item("misc_folder_combo", enabled=False, items=[], default_value="")
    dpg.configure_item("misc_template_combo", enabled=False, items=[], default_value="")
    dpg.configure_item("create_empty_button", enabled=False)

    _selected_folder_id_misc = None
    _selected_template_id_misc = None
    _selected_template_details_misc = None

    _log_callback(f"🔍 Misc Tools: Fetching folders for Document Hub ID: {_selected_hub_id_misc}...")
    _folders_data_misc = template_fetcher.get_folders_for_hub(_config, _selected_hub_id_misc,
                                                              log_callback=_log_callback)

    folder_titles_for_combo_misc = []

    hub_doc = next((doc for doc in app_state.all_documents if
                    doc.get('id') == _selected_hub_id_misc and doc.get('parent_folder_id') is None), None)
    if hub_doc and hub_doc.get('title'):
        folder_titles_for_combo_misc.append(f"{hub_doc['title']} (Root of Hub)")
    else:
        folder_titles_for_combo_misc.append(f"Root of Hub (ID: {_selected_hub_id_misc})")

    for folder in _folders_data_misc:
        if folder.get('title') and folder.get('id'):
            folder_titles_for_combo_misc.append(f"{folder['title']} (Folder ID: {folder['id']})")

    if folder_titles_for_combo_misc:
        dpg.configure_item("misc_folder_combo", items=folder_titles_for_combo_misc, enabled=True)
        dpg.set_value("misc_folder_combo", folder_titles_for_combo_misc[0])
        _log_callback(
            f"✅ Misc Tools: Found {len(folder_titles_for_combo_misc)} selectable folders/root for Hub {_selected_hub_id_misc}.")
        # No need to call folder_selected_callback_misc_internal, it will be called by dpg.set_value
    else:
        dpg.configure_item("misc_folder_combo", items=[f"Root of Hub (ID: {_selected_hub_id_misc})"], enabled=True)
        dpg.set_value("misc_folder_combo", f"Root of Hub (ID: {_selected_hub_id_misc})")
        _log_callback(
            f"❌ Misc Tools: No sub-folders found for Hub {_selected_hub_id_misc}. You can still upload directly to the hub root.")
        # No need to call folder_selected_callback_misc_internal

    # Filter templates based on those used by documents in the selected hub for compatibility
    template_ids_in_selected_hub_documents = set(doc.get('template_id') for doc in app_state.all_documents
                                                 if doc.get('document_hub_id') == _selected_hub_id_misc and doc.get(
        'template_id') is not None)

    _templates_data_misc_filtered = []
    for template in app_state.all_available_templates:
        if template.get('id') in template_ids_in_selected_hub_documents:
            _templates_data_misc_filtered.append(template)

    template_titles_for_combo_misc_items = [t.get('title', f"Untitled Template (ID: {t.get('id')})") for t in
                                            _templates_data_misc_filtered]

    if template_titles_for_combo_misc_items:
        dpg.configure_item("misc_template_combo", items=template_titles_for_combo_misc_items, enabled=True)
        _log_callback(
            f"✅ Misc Tools: Found {len(template_titles_for_combo_misc_items)} templates compatible with Hub {_selected_hub_id_misc}.")
    else:
        dpg.configure_item("misc_template_combo", items=[], enabled=False)
        _log_callback(
            f"❌ Misc Tools: No compatible templates found for Hub {_selected_hub_id_misc}. Please select a different Hub or add documents using templates to this Hub.")

    if dpg.does_item_exist("create_empty_button"):
        if _selected_folder_id_misc is not None and _selected_template_id_misc is not None:
            dpg.configure_item("create_empty_button", enabled=True)
        else:
            dpg.configure_item("create_empty_button", enabled=False)


# This function is now at the module level
def folder_selected_callback_misc_internal(sender, app_data):
    global _selected_folder_id_misc
    selected_folder_value = dpg.get_value("misc_folder_combo")
    if not selected_folder_value: return

    if "Root of Hub (ID: " in selected_folder_value:
        root_hub_id_str = selected_folder_value.split(" (ID: ")[1].rstrip(")")
        _selected_folder_id_misc = int(root_hub_id_str)
        _log_callback(
            f"✅ Misc Tools: Selected Root of Hub. Uploads will go to Hub ID: {_selected_folder_id_misc} (acting as parent folder).")
    elif "(Folder ID: " in selected_folder_value:
        folder_id_str = selected_folder_value.split(" (Folder ID: ")[1].rstrip(")")
        _selected_folder_id_misc = int(folder_id_str)
        _log_callback(f"✅ Misc Tools: Selected Folder '{selected_folder_value}'. Folder ID: {_selected_folder_id_misc}")
    else:
        _selected_folder_id_misc = None
        _log_callback(f"⚠️ Misc Tools: Could not parse folder ID from '{selected_folder_value}'. Uploads might fail.")

    if dpg.does_item_exist("create_empty_button"):
        if _selected_folder_id_misc is not None and _selected_template_id_misc is not None:
            dpg.configure_item("create_empty_button", enabled=True)
        else:
            dpg.configure_item("create_empty_button", enabled=False)


# This function is now at the module level
def template_selected_callback_misc_internal(sender, app_data):
    global _selected_template_details_misc, _selected_template_id_misc
    selected_template_title = dpg.get_value("misc_template_combo")

    _selected_template_details_misc = next(
        (t for t in app_state.all_available_templates if t.get('title') == selected_template_title), None)

    if _selected_template_details_misc:
        _selected_template_id_misc = _selected_template_details_misc.get('id')
        _log_callback(f"DEBUG: Misc Tools: Selected Template Details for '{selected_template_title}':")
        _log_callback(json.dumps(_selected_template_details_misc, indent=2))

        _log_callback(
            f"✅ Misc Tools: Template '{selected_template_title}' (ID: {_selected_template_id_misc}) selected for use.")
    else:
        _log_callback(f"⚠️ Misc Tools: Could not find details for selected template '{selected_template_title}'.")
        _selected_template_id_misc = None

    if dpg.does_item_exist("create_empty_button"):
        if _selected_folder_id_misc is not None and _selected_template_id_misc is not None:
            dpg.configure_item("create_empty_button", enabled=True)
        else:
            dpg.configure_item("create_empty_button", enabled=False)


# This function is now at the module level
def create_empty_documents_callback_internal():
    # FIX: Added a print statement here to confirm callback execution
    print("--- DEBUG: create_empty_documents_callback_internal HIT ---")

    if _selected_hub_id_misc is None or _selected_folder_id_misc is None or _selected_template_id_misc is None:
        _log_callback("❌ Please select a Document Hub, Folder, and Template in this window first.")
        return

    base_title = dpg.get_value("empty_doc_base_title")
    count = dpg.get_value("empty_doc_count")

    if not base_title:
        _log_callback("❌ Base Title cannot be empty.")
        return
    if count <= 0:
        _log_callback("❌ Number of items to create must be greater than 0.")
        return

    _log_callback(
        f"🚀 Preparing to create {count} empty documents with base title '{base_title}' in Hub {_selected_hub_id_misc}, Folder {_selected_folder_id_misc} using Template {_selected_template_id_misc}...")
    dpg.configure_item("create_empty_button", enabled=False)

    empty_document_payloads = []
    for i in range(1, count + 1):
        title = f"{base_title} #{i}"
        description = ""
        empty_document_payloads.append({
            "title": title,
            "document_hub_id": _selected_hub_id_misc,
            "parent_folder_id": _selected_folder_id_misc,
            "template_id": _selected_template_id_misc,
            "description": description,
            "custom_fields": []
        })

    upload_manager.create_empty_documents(
        _config,
        empty_document_payloads,
        log_callback=_log_callback,
        on_success_callback=_fetch_hubs_callback
    )
    dpg.configure_item("create_empty_button", enabled=True)
    _log_callback("Empty document creation process finished (check logs for details).")