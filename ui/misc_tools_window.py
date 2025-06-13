# ui/misc_tools_window.py

import dearpygui.dearpygui as dpg
from core import app_state
from utils import upload_manager, api_client, template_fetcher
import json

# --- Module-level Global Variables ---
_config = None
_log_callback = None
_fetch_hubs_callback = None
_selected_hub_id_misc = None
_selected_folder_id_misc = None
_selected_template_id_misc = None
_selected_template_details_misc = None


def create_misc_tools_window(config, log_callback, fetch_hubs_callback):
    """
    Creates the 'Miscellaneous Tools' window and its UI elements.
    """
    global _config, _log_callback, _fetch_hubs_callback
    _config = config
    _log_callback = log_callback
    _fetch_hubs_callback = fetch_hubs_callback

    with dpg.window(label="Miscellaneous Tools", tag="misc_tools_window", width=600, height=400, show=False,
                    on_close=lambda: dpg.configure_item("misc_tools_window", show=False)):
        dpg.add_text("This window provides tools for special actions, like creating empty documents.")
        dpg.add_separator()
        dpg.add_text("Document Creation Target", color=(200, 200, 255))
        with dpg.group(horizontal=True):
            dpg.add_text("Target Hub:      ")
            dpg.add_combo(items=[], tag="misc_hub_combo", width=-1, callback=hub_selected_callback_misc_internal,
                          enabled=False)
        with dpg.group(horizontal=True):
            dpg.add_text("Target Folder:   ")
            dpg.add_combo(items=[], tag="misc_folder_combo", width=-1, callback=folder_selected_callback_misc_internal,
                          enabled=False)
        with dpg.group(horizontal=True):
            dpg.add_text("Target Template: ")
            dpg.add_combo(items=[], tag="misc_template_combo", width=-1,
                          callback=template_selected_callback_misc_internal, enabled=False)
        dpg.add_separator()
        dpg.add_text("Create Empty Documents", color=(255, 255, 0))
        dpg.add_input_text(label="Base Title", tag="empty_doc_base_title", default_value="New Document via APT")
        dpg.add_input_int(label="Number to Create", tag="empty_doc_count", default_value=1, min_value=1, max_value=100)
        dpg.add_button(label="Create Empty Documents", tag="create_empty_button",
                       callback=create_empty_documents_callback_internal, enabled=False)
        dpg.add_text("Note: This uses the Hub, Folder, and Template selected above.", wrap=580, color=(150, 150, 150))


def refresh_misc_data_and_combos(sender, app_data):
    """
    This function populates the Hub dropdown using the original working logic.
    """
    if not app_state.all_documents or not app_state.all_available_templates:
        _log_callback(
            "⚠️ Misc Tools: Main data not loaded. Please ensure 'Fetch Document Hubs & Templates' is clicked in Main Window.")
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
        # Auto-select logic
        if app_state.selected_hub_id and any(
                f"(ID: {app_state.selected_hub_id})" in name for name in hub_display_names):
            matching_display_name = next(
                (name for name in hub_display_names if f"(ID: {app_state.selected_hub_id})" in name), None)
            if matching_display_name:
                dpg.set_value("misc_hub_combo", matching_display_name)
                hub_selected_callback_misc_internal(None, None)
    else:
        _log_callback("❌ Misc Tools: No Document Hubs found in loaded data.")


def hub_selected_callback_misc_internal(sender, app_data):
    """
    UPDATED: This function now correctly parses the Hub ID from both possible string formats.
    """
    global _selected_hub_id_misc, _selected_folder_id_misc, _selected_template_id_misc, _selected_template_details_misc

    selected_hub_value = dpg.get_value("misc_hub_combo")
    if not selected_hub_value: return

    # --- FIX APPLIED HERE ---
    # This logic now handles both "Title (ID: X)" and "Hub ID: X" formats.
    if " (ID: " in selected_hub_value:
        hub_id_str = selected_hub_value.split(" (ID: ")[1].rstrip(")")
    else:
        hub_id_str = selected_hub_value.replace("Hub ID: ", "")
    # --- END OF FIX ---

    _selected_hub_id_misc = int(hub_id_str)
    _log_callback(f"\n▶️ Misc Tools: Hub '{selected_hub_value}' selected. ID: {_selected_hub_id_misc}")

    dpg.configure_item("misc_folder_combo", enabled=False, items=[], default_value="")
    dpg.configure_item("misc_template_combo", enabled=False, items=[], default_value="")
    dpg.configure_item("create_empty_button", enabled=False)

    _folders_data_misc = template_fetcher.get_folders_for_hub(_config, _selected_hub_id_misc,
                                                              log_callback=_log_callback)
    folder_titles_for_combo_misc = []
    hub_doc = next((doc for doc in app_state.all_documents if
                    doc.get('id') == _selected_hub_id_misc and doc.get('parent_folder_id') is None), None)
    if hub_doc and hub_doc.get('title'):
        folder_titles_for_combo_misc.append(f"{hub_doc['title']} (Root of Hub)")
    else:
        folder_titles_for_combo_misc.append(f"Root of Hub (ID: {_selected_hub_id_misc})")
    folder_titles_for_combo_misc.extend(
        [f"{f['title']} (Folder ID: {f['id']})" for f in _folders_data_misc if f.get('title') and f.get('id')])

    dpg.configure_item("misc_folder_combo", items=folder_titles_for_combo_misc, enabled=True)
    dpg.set_value("misc_folder_combo", folder_titles_for_combo_misc[0])
    folder_selected_callback_misc_internal(None, None)

    hub_details = api_client.get_hub_details(_config, _selected_hub_id_misc, log_callback=_log_callback)
    allowed_template_ids = hub_details.get('template_ids', []) if hub_details else []
    if not allowed_template_ids:
        _log_callback(f"⚠️ Hub details did not specify templates. The template list may be empty.")

    _templates_data_misc_filtered = [t for t in app_state.all_available_templates if
                                     t.get('id') in allowed_template_ids]
    template_titles_for_combo_misc_items = [t.get('title', f"Untitled (ID: {t.get('id')})") for t in
                                            _templates_data_misc_filtered]

    if template_titles_for_combo_misc_items:
        dpg.configure_item("misc_template_combo", items=template_titles_for_combo_misc_items, enabled=True)
    else:
        dpg.configure_item("misc_template_combo", items=[], enabled=False)
        _log_callback(f"❌ No compatible templates found for Hub {_selected_hub_id_misc} based on its configuration.")


def folder_selected_callback_misc_internal(sender, app_data):
    global _selected_folder_id_misc
    selected_folder_value = dpg.get_value("misc_folder_combo")
    if not selected_folder_value: return

    if "(Root of Hub)" in selected_folder_value:
        _selected_folder_id_misc = _selected_hub_id_misc
    elif "(Folder ID: " in selected_folder_value:
        _selected_folder_id_misc = int(selected_folder_value.split(" (Folder ID: ")[1].rstrip(")"))

    if _selected_folder_id_misc and _selected_template_id_misc:
        dpg.configure_item("create_empty_button", enabled=True)


def template_selected_callback_misc_internal(sender, app_data):
    global _selected_template_details_misc, _selected_template_id_misc
    selected_template_title = dpg.get_value("misc_template_combo")
    _selected_template_details_misc = next(
        (t for t in app_state.all_available_templates if t.get('title') == selected_template_title), None)
    if _selected_template_details_misc:
        _selected_template_id_misc = _selected_template_details_misc.get('id')
    else:
        _selected_template_id_misc = None

    if _selected_folder_id_misc and _selected_template_id_misc:
        dpg.configure_item("create_empty_button", enabled=True)
    else:
        dpg.configure_item("create_empty_button", enabled=False)


def create_empty_documents_callback_internal():
    if not all([_selected_hub_id_misc, _selected_folder_id_misc, _selected_template_id_misc]):
        _log_callback("❌ Please select a Document Hub, Folder, and a valid Template first.")
        return

    base_title = dpg.get_value("empty_doc_base_title")
    count = dpg.get_value("empty_doc_count")
    dpg.configure_item("create_empty_button", enabled=False)

    payloads = [{
        "title": f"{base_title} #{i + 1}",
        "document_hub_id": _selected_hub_id_misc,
        "parent_folder_id": _selected_folder_id_misc,
        "template_id": _selected_template_id_misc,
        "description": "",
        "custom_fields": []
    } for i in range(count)]

    upload_manager.create_empty_documents(
        _config,
        payloads,
        log_callback=_log_callback,
        on_success_callback=_fetch_hubs_callback
    )
    dpg.configure_item("create_empty_button", enabled=True)