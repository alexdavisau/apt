# utils/excel_writer.py

import openpyxl
from tkinter import messagebox


def create_template_excel(headers: list, hub_id: int, folder_id: int, template_id: int, output_path: str,
                          log_callback=print):
    """
    Creates an Excel file with a given list of headers and includes metadata.
    """
    if not headers:
        messagebox.showwarning("Warning", "The selected template has no custom fields to create an Excel file from.")
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
        metadata_sheet['A3'] = "Source Template ID"
        metadata_sheet['B3'] = template_id

        workbook.save(output_path)
        log_callback(f"✅ Successfully created validated Excel file at: {output_path}")
        messagebox.showinfo("Success", f"Successfully created validated Excel file at:\n{output_path}")

    except Exception as e:
        log_callback(f"❌ Failed to create Excel file: {e}")
        messagebox.showerror("Error", f"Failed to create Excel file: {e}")