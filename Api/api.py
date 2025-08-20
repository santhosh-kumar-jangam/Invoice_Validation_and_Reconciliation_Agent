# main.py
import os
import sqlite3, re, json, uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
from google.api_core import exceptions

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from typing import List
from rootagent.agent import root_agent
from dotenv import load_dotenv
import json
import re
# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Load both bucket names from your .env file
BANK_STATEMENT_BUCKET = os.getenv("BANK_STATEMENT_BUCKET")
INVOICE_BUCKET = os.getenv("SOURCE_BUCKET") # New variable for the invoice bucket
GCP_CREDENTIALS_PATH = os.getenv("gcp_credentials_path")

# --- Initialization ---
# Initialize FastAPI app with a more descriptive title
app = FastAPI(title="Multi-Bucket PDF Upload Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize Google Cloud Storage client
storage_client = None
try:
    if not GCP_CREDENTIALS_PATH:
        raise ValueError("gcp_credentials_path environment variable not set.")
    storage_client = storage.Client.from_service_account_json(GCP_CREDENTIALS_PATH)
except Exception as e:
    print(f"Error initializing GCS client: {e}")
    # The app will fail to start if the client can't be initialized, which is good.

# --- Reusable Helper Function (Refactored Logic) ---
def extract_json_from_response(text: str) -> dict:
    """
    Finds and parses the last, most complete JSON object or array from a string.
    """
    # Regex to find JSON wrapped in ```json ... ``` or just standalone
    # It looks for a string starting with { or [ and ending with } or ]
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\}|\[[\s\S]*\])', text)

    if not json_match:
        # If regex fails, try a simpler approach: find the last occurrence of '{' or '['
        last_brace = text.rfind('{')
        last_bracket = text.rfind('[')
        
        if last_brace == -1 and last_bracket == -1:
             raise ValueError("No valid JSON structure found in the agent's response.")

        start_index = max(last_brace, last_bracket)
        json_string = text[start_index:]
    else:
        # The regex found a match. Get the content from the appropriate group.
        json_string = json_match.group(1) or json_match.group(2)
        
    try:
        # Parse the found string into a Python dictionary or list
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse extracted JSON: {e}\n\nExtracted string was:\n{json_string}")
    
async def _upload_file_to_gcs(file: UploadFile, bucket_name: str):
    """
    A helper function to upload a file to a specified GCS bucket.
    """
    # 1. Pre-flight checks
    if not storage_client:
        raise HTTPException(
            status_code=500,
            detail="GCS client is not initialized. Check server configuration."
        )
    if not bucket_name:
        raise HTTPException(
            status_code=500,
            detail=f"Target GCS bucket name is not configured on the server."
        )
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDFs are accepted. Received: {file.content_type}"
        )

    try:
        # 2. Get the GCS bucket
        bucket = storage_client.get_bucket(bucket_name)

        # 3. Create a new blob (GCS object)
        blob = bucket.blob(file.filename)
        
        # 4. Read the file and upload it
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)

        # 5. Return success response
        return {
            "message": f"File '{file.filename}' uploaded successfully to bucket '{bucket_name}'.",
            "filename": file.filename,
            "gcs_path": f"gs://{bucket_name}/{blob.name}",
            "public_url": blob.public_url
        }
    except exceptions.NotFound:
        raise HTTPException(
            status_code=404,
            detail=f"The bucket '{bucket_name}' does not exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during file upload: {str(e)}"
        )


@app.post("/api/upload/bankstatement", tags=["Bank Statements"])
async def upload_bank_statement(file: UploadFile = File(...)):
    """
    Accepts a bank statement PDF and uploads it to the bank statements bucket.
    """
    return await _upload_file_to_gcs(file=file, bucket_name=BANK_STATEMENT_BUCKET)

@app.post("/api/upload/invoice", tags=["Invoices"])
async def upload_invoice(file: UploadFile = File(...)):
    """
    Accepts an invoice PDF and uploads it to the invoices bucket.
    """
    return await _upload_file_to_gcs(file=file, bucket_name=INVOICE_BUCKET)


@app.post("/api/run")
async def run_reconciliation_agent():
    try:
        APP_NAME = "reconciliation"
        USER_ID = "user1"
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
        session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
        content = Content(role='user', parts=[Part(text="Run the Reconciliation pipeline")])
        events = runner.run_async(user_id=USER_ID, session_id=session.id, new_message=content)

        full_response_text = "No final response was received from the agent."
        async for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    full_response_text = "".join(part.text for part in event.content.parts)
                else:
                    full_response_text = "Final response event had no content."
                break
        
        try:
            clean_json_response = extract_json_from_response(full_response_text)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Could not parse JSON from agent response. Error: {e}")
        
        # --- MODIFIED SECTION START ---

        full_json_object = clean_json_response

        print("***********8888888888888888888")
        print(full_json_object)
        print("***********8888888888888888888")

        results_list = full_json_object.get("audit_report", []) # Use .get with a default value
 
        db_path = os.getenv("DB_PATH")
        run_id = str(uuid.uuid4())
 
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
           
            for result_item in results_list:
                # Prepare payment dates for insertion
                payment_dates_val = result_item.get("payment_date")
                if isinstance(payment_dates_val, list):
                    # If it's a list, join it into a comma-separated string
                    payment_dates_to_insert = ", ".join(map(str, payment_dates_val))
                elif payment_dates_val == "N/A":
                    # If it's the string "N/A", store it as NULL in the database
                    payment_dates_to_insert = None
                else:
                    # Otherwise, use the value as is (it's likely a string or None)
                    payment_dates_to_insert = payment_dates_val
                
                # Prepare transaction IDs for insertion (same logic)
                transaction_ids_val = result_item.get("transaction_id")
                if isinstance(transaction_ids_val, list):
                    transaction_ids_to_insert = ", ".join(map(str, transaction_ids_val))
                elif transaction_ids_val == "N/A":
                    transaction_ids_to_insert = None
                else:
                    transaction_ids_to_insert = transaction_ids_val

                # Prepare amount paid, handling "N/A"
                amount_paid_value = result_item.get("amount_paid")
                amount_paid_to_insert = None if amount_paid_value == "N/A" else amount_paid_value

                # Build the final tuple for insertion
                data_to_insert = (
                    run_id,
                    result_item.get("invoice_number"),
                    result_item.get("vendor_name"),
                    result_item.get("total_amount"),
                    payment_dates_to_insert,     # Use the processed string value
                    transaction_ids_to_insert,   # Use the processed string value
                    amount_paid_to_insert,
                    result_item.get("status"),
                    result_item.get("verdict"),
                    result_item.get("conclusion")
                )
               
                cursor.execute("""
                    INSERT INTO reconciliation_results (
                        run_id, invoice_number, vendor_name, claimed_total,
                        payment_dates, transaction_ids, amount_paid,
                        status, verdict, conclusion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data_to_insert)

                conn.commit()

        return full_json_object

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred while running the agent: {str(e)}"
        )
    
def get_db_connection():
    """Opens a new database connection and closes it when done."""
    try:
        DATABASE_PATH = os.getenv("DB_PATH", "database.db")
        conn = sqlite3.connect(DATABASE_PATH)
        # This makes the results behave like dictionaries (e.g., row['column_name'])
        conn.row_factory = sqlite3.Row 
        yield conn
    except sqlite3.Error as e:
        # If the database file can't be opened, raise an HTTP exception.
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.get(
    "/run-ids",
    response_model=List[str],
    summary="Get All Unique Run IDs",
    tags=["Reconciliation"]
)
def get_all_run_ids(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retrieves a list of all unique `run_id`s from the
    `reconciliation_results` table by executing a raw SQL command.
    """
    try:
        cursor = conn.cursor()
        
        # The raw SQL command
        sql_command = "SELECT DISTINCT run_id FROM reconciliation_results"
        
        cursor.execute(sql_command)
        
        # fetchall() returns a list of row objects.
        # This list comprehension efficiently extracts the 'run_id' from each row.
        results = cursor.fetchall()
        run_ids = [row["run_id"] for row in results]
        
        return run_ids
    except sqlite3.OperationalError as e:
        # This error typically means the table doesn't exist.
        raise HTTPException(
            status_code=500, 
            detail=f"SQL Error: {e}."
        )
    
@app.get(
    "/run-reports"
)
def get_all_run_reports(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retrieves a list of all runs from the
    `reconciliation_results` table by executing a raw SQL command.
    """
    try:
        cursor = conn.cursor()
        
        # The raw SQL command
        sql_command = "SELECT * FROM reconciliation_results"
        
        cursor.execute(sql_command)
        
        # fetchall() returns a list of row objects.
        # This list comprehension efficiently extracts the 'run_id' from each row.
        results = cursor.fetchall()
        run_reports = [row for row in results]
        
        return run_reports
    except sqlite3.OperationalError as e:
        # This error typically means the table doesn't exist.
        raise HTTPException(
            status_code=500, 
            detail=f"SQL Error: {e}."
        )
    

@app.get("/api/invoices")
def get_invoices():
    try:
        db_path = os.getenv("DB_PATH", "database.db")
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
           
            cursor = conn.cursor()
           
            query = """
                SELECT
                    invoice_number,
                    invoice_date,
                    due_date,
                    vendor_name,
                    client_name,
                    total_amount
                FROM
                    invoices
            """
           
            cursor.execute(query)
            results = cursor.fetchall()
 
            invoices = [dict(row) for row in results]
           
            return invoices
 
    except sqlite3.Error as e:
        # Handle potential database errors (e.g., table not found)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {e}"
        )
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}"
        )
    

@app.get("/api/bank/transactions")
def get_transactions():
    try:
        db_path = os.getenv("DB_PATH", "database.db")
        with sqlite3.connect(db_path) as conn:
            # This makes cursor results accessible by column name (like a dict)
            conn.row_factory = sqlite3.Row
           
            cursor = conn.cursor()
           
            # Fetch the most recent transactions first
            query = """
                SELECT
                    transaction_id,
                    invoice_number,
                    description,
                    transaction_date,
                    debit_amount,
                    status
                FROM
                    bank_transactions
            """
           
            cursor.execute(query)
            results = cursor.fetchall()
 
            # Convert the list of sqlite3.Row objects to a list of dicts
            # This is necessary for FastAPI to build the Pydantic response model
            transactions = [dict(row) for row in results]
           
            return transactions
 
    except sqlite3.Error as e:
        # Handle potential database errors (e.g., table not found)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {e}"
        )
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}"
        )

@app.get("/api/report/{runId}")
def get_report_by_run_id(runId: str):
    """
    Retrieves all reconciliation results associated with a specific run ID.
    """
    try:
        # Assumes DB_PATH is set in your .env file
        db_path = os.getenv("DB_PATH")
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query to fetch all results for the given run_id
            query = """
                SELECT 
                    run_id, invoice_number, vendor_name, claimed_total, 
                    payment_dates, transaction_ids, amount_paid, 
                    status, verdict, conclusion, processed_at
                FROM 
                    reconciliation_results 
                WHERE 
                    run_id = ?
            """
            
            cursor.execute(query, (runId,))
            results = cursor.fetchall()
            
            # If the query returns no results, the run ID was not found
            if not results:
                raise HTTPException(
                    status_code=404,
                    detail=f"No report found for run ID: {runId}"
                )
            
            # Convert the database rows into a list of dictionaries for the JSON response
            report_items = [dict(row) for row in results]
            
            return report_items

    except sqlite3.Error as e:
        # Handle database-specific errors
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {e}"
        )
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

 
