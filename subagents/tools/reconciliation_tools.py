# subagents/tools/reconciliation_tools.py
import os, io, json
from google.cloud.storage import Client
import pdfplumber
from dotenv import load_dotenv
load_dotenv()

def get_all_invoice_jsons() -> str:
    """
    Finds all processed invoice JSON files and returns them as a single JSON list string.
    """
    print("--- [Tool] Fetching all processed invoice JSONs... ---")
    try:
        client = Client.from_service_account_json(os.getenv("gcp_credentials_path"))
        bucket = client.bucket(os.getenv("TARGET_BUCKET"))
        blobs = [b for b in bucket.list_blobs() if b.name.endswith('.json')]
        if not blobs: return "[]"
        all_invoices = [json.loads(blob.download_as_string()) for blob in blobs]
        return json.dumps(all_invoices)
    except Exception as e:
        return f'{{"error": "Error fetching invoice JSONs: {str(e)}"}}'

def extract_text_from_bank_statement() -> str:
    """
    Finds the bank statement in GCS, extracts all text, and returns it as a string.
    """
    print("--- [Tool] Extracting text from bank statement PDF... ---")
    try:
        client = Client.from_service_account_json(os.getenv("gcp_credentials_path"))
        bucket = client.bucket(os.getenv("BANK_STATEMENT_BUCKET"))
        blobs = list(bucket.list_blobs())
        if not blobs: return "Error: No bank statement file found."
        
        content = blobs[0].download_as_bytes()
        full_text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: full_text += page_text + "\n"
        return full_text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"