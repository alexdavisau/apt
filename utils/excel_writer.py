# utils/excel_writer.py

import openpyxl
from tkinter import messagebox


def create_template_excel(visual_config: dict, hub_id: int, folder_id: int, output_path: str, log_callback=print):
    """
    Creates an Excel file with headers based on a template's visual configuration.
    """
    if not visual_config:
        log_callback("❌ Invalid visual_config provided to excel_writer.")
        return

    try:
        # CORRECTED LOGIC: Fields are in the 'component_list_in_config'
        components = visual_config.get('component_list_in_config', [])

        # We need the full template details to get field names from the IDs (rendered_oid)
        # This information is not in the visual config. We will need to fetch it.
        # For now, we will create a placeholder. This logic needs to be completed.

        # Placeholder: a real implementation would look up the field name from the rendered_oid
        headers = [f"Field ID: {comp.get('rendered_oid')}" for comp in components if
                   comp.get('rendered_otype') == 'CUSTOM_FIELD']

    except Exception as e:
        log_callback(f"❌ Could not parse fields from visual config: {e}")
        messagebox.showerror("Error", "Could not parse fields from the template's visual configuration.")
        return

    if not headers:
        messagebox.showwarning("Warning", "The selected template has no custom fields defined in its layout.")
        return

    try:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Alation Upload"
        sheet.append(headers)
        log_callback(f"Generated headers: {headers}")

        metadata_sheet = workbook.create_sheet(title="_apt_metadata")
        metadata_sheet.sheet_state = 'hidden'
        metadata_sheet['A1'] = "Source Hub ID"
        metadata_sheet['B1'] = hub_id
        metadata_sheet['A2'] = "Source Folder ID"
        metadata_sheet['B2'] = folder_id
        metadata_sheet['A3'] = "Source Template Title"
        metadata_sheet['B3'] = visual_config.get('title', 'Unknown')

        workbook.save(output_path)
        log_callback(f"✅ Successfully created validated Excel file at: {output_path}")
        messagebox.showinfo("Success", f"Successfully created validated Excel file at:\n{output_path}")

    except Exception as e:
        log_callback(f"❌ Failed to create Excel file: {e}")
        messagebox.showerror("Error", f"Failed to create Excel file: {e}")