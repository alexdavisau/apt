import time
from pathlib import Path
import pandas as pd
import requests
import json
from urllib.parse import urljoin
from utils import alation_lookup
from utils.api_client import DOCUMENTS_CACHE_PATH, TEMPLATES_CACHE_PATH

LOG_PATH = Path("logs")


# This function is now the primary entry point for Excel uploads.
def upload_documents_from_excel(config: dict, df_to_upload: pd.DataFrame, document_hub_id: int, parent_folder_id: int,
                                template_details: dict, log_callback=print, on_success_callback: callable = None):
    """
    Reads document data from a DataFrame (typically from Excel) and uploads each document to Alation.
    Handles different custom field types, including OBJECT_SET lookup.
    """
    # This try-except block is for errors specific to reading/processing the Excel DataFrame
    try:
        if df_to_upload.empty:
            log_callback("❌ DataFrame is empty. No documents to upload.")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            log_file_name = LOG_PATH / f"upload_log_excel_{timestamp}.txt"
            with open(log_file_name, "w") as f:
                f.write(f"--- Excel upload from '{getattr(df_to_upload, '_file_path', 'unknown_file')}' Log ---\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write("No documents to upload (empty DataFrame).\n")
            return

        field_name_to_details_map = {}
        if 'fields' in template_details and template_details['fields']:
            for field in template_details['fields']:
                field_name_key = field.get('name_singular') or field.get(
                    'name_plural') or f"Field ID: {field.get('id')}"
                field_name_to_details_map[field_name_key] = field

        documents_to_upload_payloads = []

        for index, row in df_to_upload.iterrows():
            document_title = row.get("Title")
            document_description = row.get("Description", "")

            if not document_title:
                log_callback(
                    f"⚠️ Skipping row {index + 2}: 'Title' column is missing or empty. Each document must have a title.")
                continue

            log_callback(f"Processing document: '{document_title}'")

            custom_fields_payload = []
            for col_header, field_details in field_name_to_details_map.items():
                alation_field_id = field_details['id']
                field_type = field_details['field_type']
                builtin_name = field_details.get('builtin_name')

                if builtin_name in ["description", "title"]:
                    log_callback(
                        f"DEBUG: Skipping built-in field '{builtin_name}' (ID: {alation_field_id}) from custom_fields payload, as it's handled at top level.")
                    continue

                if col_header in row:
                    field_value = row[col_header]

                    if field_type == "RICH_TEXT":
                        if pd.notna(field_value):
                            custom_fields_payload.append({
                                "field_id": alation_field_id,
                                "value": str(field_value)
                            })
                    elif field_type == "PICKER":
                        if pd.notna(field_value):
                            custom_fields_payload.append({
                                "field_id": alation_field_id,
                                "value": str(field_value)
                            })
                    elif field_type == "OBJECT_SET":
                        if pd.notna(field_value):
                            object_set_values = []
                            names_from_excel = []
                            if field_details.get('allow_multiple', False):
                                names_from_excel = [name.strip() for name in str(field_value).split(',') if
                                                    name.strip()]
                            else:
                                names_from_excel = [str(field_value).strip()]

                            otype_hint_for_lookup = None
                            allowed_otypes_from_template = field_details.get('allowed_otypes')
                            if allowed_otypes_from_template and len(allowed_otypes_from_template) == 1:
                                if allowed_otypes_from_template[0] == 'user':
                                    otype_hint_for_lookup = 'user'
                                elif allowed_otypes_from_template[0] == 'groupprofile':
                                    otype_hint_for_lookup = 'group'

                            for name in names_from_excel:
                                looked_up_object = alation_lookup.lookup_alation_object(config, name,
                                                                                        otype_hint=otype_hint_for_lookup,
                                                                                        log_callback=log_callback)
                                if looked_up_object:
                                    object_set_values.append(looked_up_object)
                                else:
                                    fail_msg = f"❌ FAILED OBJECT SET LOOKUP: Could not find Alation object for '{name}' for field '{col_header}' (Original Value: '{field_value}'). Skipping this specific entry for this document."
                                    log_callback(fail_msg)
                                    upload_log_entries.append(f"FAILED OBJECT SET: Doc '{document_title}' - {fail_msg}")

                            if object_set_values:
                                custom_fields_payload.append({
                                    "field_id": alation_field_id,
                                    "value": object_set_values
                                })
                            else:
                                log_callback(
                                    f"⚠️ Warning: No valid Alation objects found for '{col_header}' (Value: '{field_value}'). Omitting this field from payload for this document.")
                        pass
                    else:
                        if pd.notna(field_value):
                            custom_fields_payload.append({
                                "field_id": alation_field_id,
                                "value": str(field_value)
                            })

            document_payload = {
                "title": document_title,
                "document_hub_id": document_hub_id,
                "parent_folder_id": parent_folder_id,
                "template_id": template_details.get('id'),
                "description": document_description,
                "custom_fields": custom_fields_payload
            }
            documents_to_upload_payloads.append(document_payload)

        _perform_bulk_upload(
            config=config,
            documents_to_upload=documents_to_upload_payloads,
            log_callback=log_callback,
            on_success_callback=on_success_callback,
            upload_log_entries=upload_log_entries,
            context_name=f"Excel upload from '{getattr(df_to_upload, '_file_path', 'unknown_file')}'"
        )
    except Exception as e:
        log_callback(f"❌ Error reading or processing Excel file: {e}")
        import traceback
        traceback.print_exc()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file_name = LOG_PATH / f"upload_log_excel_error_{timestamp}.txt"
        with open(log_file_name, "w") as f:
            f.write(
                f"--- Excel upload from '{getattr(df_to_upload, '_file_path', 'unknown_file')}' (Failed due to processing error) ---\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Error: {e}\n")
            f.write(traceback.format_exc())


# This function is now the primary entry point for Excel uploads.
upload_documents = upload_documents_from_excel


# This is the actual bulk upload helper. It is at the top level of the module.
def _perform_bulk_upload(config: dict, documents_to_upload: list, log_callback=print,
                         on_success_callback: callable = None, upload_log_entries: list = None,
                         context_name: str = "Bulk upload", log_file_name: Path = None):
    """
    Internal helper to perform the actual bulk API call and handle responses/logging.
    This is extracted to avoid code duplication between Excel upload and empty document creation.
    """
    LOG_PATH.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    if log_file_name is None:
        log_file_name = LOG_PATH / f"upload_log_{context_name.replace(' ', '_').replace(':', '')}_{timestamp}.txt"

    if upload_log_entries is None:
        upload_log_entries = []

    api_url = f"{config['alation_url'].rstrip('/')}/integration/v2/document/"
    headers = {
        "TOKEN": config["access_token"],
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    uploaded_count = 0
    failed_count = 0

    if not documents_to_upload:
        log_callback(f"No documents found for {context_name}. Skipping API call.")
        with open(log_file_name, "w") as f:
            f.write(f"--- {context_name} Log ---\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("No documents to upload.\n")
        return

    try:
        log_callback(
            f"DEBUG: Sending bulk payload for '{context_name}': {json.dumps(documents_to_upload[:min(5, len(documents_to_upload))], indent=2)}...")
        response = requests.post(api_url, headers=headers, json=documents_to_upload, timeout=120)

        if response.status_code in (200, 201, 202):
            response_data = response.json()

            if response.status_code == 202 and response_data.get('job_id'):
                job_id = response_data.get('job_id')
                uploaded_count = len(documents_to_upload)
                log_callback(f"✅ {context_name} initiated successfully. Job ID: {job_id}. Check Alation for status.")
                upload_log_entries.append(f"SUCCESS: {context_name} initiated. Job ID: {job_id}")
            elif isinstance(response_data, list):
                for doc_response in response_data:
                    uploaded_count += 1
                    new_doc_id = doc_response.get('id', 'N/A')
                    doc_title = doc_response.get('title', 'N/A')
                    log_callback(f"✅ Uploaded '{doc_title}' (ID: {new_doc_id})")
                    upload_log_entries.append(f"SUCCESS: '{doc_title}' (ID: {new_doc_id})")
            else:
                uploaded_count = len(documents_to_upload)
                log_callback(
                    f"✅ {context_name} successful, but unexpected response format. Status: {response.status_code}, Response: {response.text}")
                upload_log_entries.append(
                    f"SUCCESS: {context_name}, unexpected response. Status: {response.status_code}, Response: {response.text}")

            log_callback("Invalidating document cache as upload was successful...")
            DOCUMENTS_CACHE_PATH.unlink(missing_ok=True)
            if on_success_callback:
                log_callback("Triggering UI refresh callback.")
                on_success_callback()

        else:
            failed_count = len(documents_to_upload)
            error_msg = f"Failed to perform {context_name}: {response.status_code} - {response.text}"
            log_callback(f"❌ {error_msg}")
            upload_log_entries.append(f"FAILED: {context_name} - {response.status_code} - {response.text}")

    except requests.RequestException as e:
        failed_count = len(documents_to_upload)
        error_msg = f"Connection error during {context_name}: {e}"
        log_callback(f"❌ {error_msg}")
        upload_log_entries.append(f"FAILED: {context_name} - Connection Error: {e}")

    with open(log_file_name, "w") as f:
        f.write(f"--- {context_name} Log ---\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total documents prepared: {len(documents_to_upload)}\n")
        f.write(f"Successfully uploaded: {uploaded_count}\n")
        f.write(f"Failed uploads: {failed_count}\n\n")
        f.write("--- Individual Upload Results / Details ---\n")
        for entry in upload_log_entries:
            f.write(f"{entry}\n")

    log_callback(f"✅ {context_name} complete. See log file: {log_file_name}")


def create_empty_documents(config: dict, document_payloads: list, log_callback=print,
                           on_success_callback: callable = None):
    """
    Uploads a list of pre-constructed document payloads (e.g., empty documents) to Alation.
    This is a wrapper around _perform_bulk_upload for specific use cases.
    """
    _perform_bulk_upload(
        config=config,
        documents_to_upload=document_payloads,
        log_callback=log_callback,
        on_success_callback=on_success_callback,
        context_name="Empty document creation"
    )