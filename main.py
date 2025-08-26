# main.py (or your FastAPI app file)

import io
import os
from dotenv import load_dotenv
import pdfplumber
from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import storage, exceptions # Make sure you have these imports for your GCS function

# --- Import your custom modules ---
from subagents.tools.inv_parser_tool import extract_invoice_data_from_text
from subagents.tools.database_tools import save_invoice_data

# --- Placeholder for your GCS client and constants ---
# This should be initialized once when your app starts
load_dotenv()
storage_client = storage.Client.from_service_account_json(os.getenv("gcp_credentials_path"))
INVOICE_BUCKET = os.getenv("SOURCE_BUCKET") 

app = FastAPI()


async def _upload_file_to_gcs(file: UploadFile, bucket_name: str):
    """
    A helper function to upload a file to a specified GCS bucket.
    """
    if not storage_client:
        raise HTTPException(status_code=500, detail="GCS client not initialized.")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="Target GCS bucket name not configured.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only PDFs are accepted. Received: {file.content_type}")

    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file.filename)
        
        # This function reads the file stream. We must seek(0) before calling it if the stream was read previously.
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)

        return {
            "message": f"File '{file.filename}' uploaded successfully to bucket '{bucket_name}'.",
            "filename": file.filename,
            "gcs_path": f"gs://{bucket_name}/{blob.name}",
            "public_url": blob.public_url
        }
    except exceptions.NotFound:
        raise HTTPException(status_code=404, detail=f"The bucket '{bucket_name}' does not exist.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during file upload: {str(e)}")


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Helper function to extract text from PDF content in memory."""
    full_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text.strip()


@app.post("/api/upload/invoice", tags=["Invoices"])
async def upload_invoice(file: UploadFile = File(...)):
    """
    Accepts an invoice PDF, uploads it to GCS, extracts key fields using a 
    deterministic Python parser, and saves them to the database.
    """
    # 1. Read file content into memory ONCE. This is for text extraction.
    content_bytes = await file.read()
    
    
    await file.seek(0)
    
   
    upload_result = await _upload_file_to_gcs(file=file, bucket_name=INVOICE_BUCKET)

    # 4. Extract text from the content we read into memory earlier.
    raw_text = extract_text_from_pdf_bytes(content_bytes)
    if not raw_text:
        return {
            "message": "File uploaded to GCS, but no text could be extracted for processing.",
            "gcs_details": upload_result,
            "extracted_data": None
        }

    # 5. Parse the text using the deterministic Python function.
    extracted_data = extract_invoice_data_from_text(raw_text)

    # 6. Save the extracted data to the database if an invoice number was found.
    if extracted_data.get("invoice_number"):
        db_result = save_invoice_data(extracted_data)
        if "error" in db_result.lower():
            print(f"WARNING: File uploaded, but DB save failed: {db_result}")
    else:
        print(f"WARNING: No invoice number found in {file.filename}, skipping database save.")

    # 7. Return a comprehensive response.
    return {
        "message": "Invoice uploaded and processed successfully.",
        "gcs_details": upload_result,
        "extracted_data": extracted_data
    }