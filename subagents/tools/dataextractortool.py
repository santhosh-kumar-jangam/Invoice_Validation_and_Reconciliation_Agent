from google.cloud.storage import Client
import os
import io
import json
import pdfplumber

from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any

def list_gcs_invoices() -> Dict[str, Any]:
    """
    Lists all invoice file names from the source Google Cloud Storage (GCS) bucket.

    Returns a status dictionary with:
        - "success" (bool): True if invoices were listed successfully, False otherwise.
        - "data" (List[str] or None): The list of invoice blob names, or None on failure.
        - "error" (str or None): Error message if failure occurred.
    """
    try:
        service_account_key_path = os.getenv("gcp_credentials_path")
        bucket_name = os.getenv("SOURCE_BUCKET")

        client = Client.from_service_account_json(service_account_key_path)
        bucket = client.bucket(bucket_name)
        
        blobs = bucket.list_blobs()
        files = [blob.name for blob in blobs]

        return {"success": True, "data": files, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
    

def extract_invoice_content(file_name: str) -> Dict[str, Any]:
    """
    Extract text and table content from a PDF invoice stored in GCS.

    Args:
        file_name (str): The name of the invoice file in the bucket.

    Returns a status dictionary with:
        - "success" (bool): True if extraction succeeded, False otherwise.
        - "data" (str or None): Extracted invoice content, or None on failure.
        - "error" (str or None): Error message if failure occurred.
    """

    try:
        text_content = ""
        table_content = ""

        service_account_key_path = os.getenv("gcp_credentials_path")
        bucket_name = os.getenv("SOURCE_BUCKET")

        client = Client.from_service_account_json(service_account_key_path)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download PDF file as bytes
        pdf_bytes = blob.download_as_bytes()

        # Open with pdfplumber from bytes
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                # Extract normal text
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"

                # Extract table content as text
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            row_text = " | ".join([cell if cell else "" for cell in row])
                            table_content += row_text + "\n"

        content = f"--- TEXT CONTENT ---\n{text_content.strip()}\n--- TABLE CONTENT ---\n{table_content.strip()}"

        return {"success": True, "data": content.strip(), "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


def upload_json_to_gcs(json_content: dict, file_name: str) -> Dict[str, Any]:
    """
    Upload JSON content to a GCS bucket as a json file.

    Args:
        json_content (Dict): The JSON-serializable Python dictionary to upload.
        file_name (str): The original PDF file name.

    Returns a status dictionary with:
        - "success" (bool): True if upload succeeded, False otherwise.
        - "data" (str or None): GCS path of uploaded file, or None on failure.
        - "error" (str or None): Error message if failure occurred.
    """

    try:
        service_account_key_path = os.getenv("gcp_credentials_path")
        bucket_name = os.getenv("TARGET_BUCKET")

        client = Client.from_service_account_json(service_account_key_path)
        bucket = client.bucket(bucket_name)

        json_filename = file_name.replace(".pdf", ".json")
        blob = bucket.blob(json_filename)

        json_data = json.dumps(json_content, indent=4)
        blob.upload_from_string(json_data, content_type="application/json")
        
        return {"success": True, "data": "JSON file successfully uploaded", "error": None}

    except Exception as e:
        return {"success": False, "data": "Failed to upload JSON file", "error": str(e)}