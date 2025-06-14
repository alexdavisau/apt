# utils/excel_writer.py

import openpyxl
from tkinter import messagebox

def create_template_excel(template_details: dict, output_path: str, log_callback=print):
    """
    Creates an Excel file with headers based on an Alation template's custom fields.

    Args:
        template_details (dict): The full dictionary of the selected template.
        output_path (str): The path where the Excel file will be saved.
        log_callback (callable): A function to handle logging.
    """
    if not template_details or 'custom_fields' not in template_details:
        log_callback("❌ Invalid template details provided.")
        messagebox.showerror("Error", "Invalid template details provided.")
        return

    custom_fields = template_details.get('custom_fields', [])
    if not custom_fields:
        log_callback("⚠️ The selected template has no custom fields to create columns.")
        messagebox.showwarning("Warning", "The selected template has no custom fields.")
        return

    # Extract the 'name' of each custom field to use as a header
    headers = [field.get('name', 'Unnamed Field') for field in custom_fields]

    try:
        # Create a new Excel workbook and select the active sheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Alation Upload"

        # Append the headers to the first row
        sheet.append(headers)
        log_callback(f"Generated headers: {headers}")

        # Save the workbook to the specified path
        workbook.save(output_path)
        log_callback(f"✅ Successfully created validated Excel file at: {output_path}")
        messagebox.showinfo("Success", f"Successfully created validated Excel file at:\n{output_path}")

    except Exception as e:
        log_callback(f"❌ Failed to create Excel file: {e}")
        messagebox.showerror("Error", f"Failed to create Excel file: {e}")