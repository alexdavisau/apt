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
        # Fields are nested within the visual config's layout structure
        fields = visual_config.get('layout', {}).get('layout', {}).get('body', [])
        if not fields:
            raise ValueError("No 'body' or 'layout' section found in visual config")

        # Extract the 'name' from each field definition
        headers = [field.get('name', 'Unnamed Field') for field in fields if 'name' in field]

    except (AttributeError, ValueError) as e:
        log_callback(f"❌ Could not parse fields from visual config: {e}")
        messagebox.showerror("Error", "Could not parse fields from the selected template's visual configuration.")
        return

    if not headers:
        log_callback("⚠️ The selected template's visual config has no fields to create columns.")
        messagebox.showwarning("Warning", "The selected template has no fields defined in its layout.")
        return

    template_id = visual_config.get('template_id')

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
        metadata_sheet['A3'] = "Source Template ID"
        metadata_sheet['B3'] = template_id

        workbook.save(output_path)
        log_callback(f"✅ Successfully created validated Excel file at: {output_path}")
        messagebox.showinfo("Success", f"Successfully created validated Excel file at:\n{output_path}")

    except Exception as e:
        log_callback(f"❌ Failed to create Excel file: {e}")
        messagebox.showerror("Error", f"Failed to create Excel file: {e}")