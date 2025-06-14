# utils/excel_writer.py

import openpyxl
from tkinter import messagebox


def create_template_excel(template_details: dict, hub_id: int, folder_id: int, output_path: str, log_callback=print):
    """
    Creates an Excel file with headers based on an Alation template's custom fields
    and includes a hidden sheet with metadata.
    """
    if not template_details or 'custom_fields' not in template_details:
        log_callback("❌ Invalid template details provided to excel_writer.")
        messagebox.showerror("Error", "Invalid template details passed to Excel writer.")
        return

    custom_fields = template_details.get('custom_fields', [])
    if not custom_fields:
        log_callback("⚠️ The selected template has no custom fields to create columns.")
        messagebox.showwarning("Warning", "The selected template has no custom fields.")
        return

    headers = [field.get('name', 'Unnamed Field') for field in custom_fields]
    template_id = template_details.get('id')

    try:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Alation Upload"
        sheet.append(headers)

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