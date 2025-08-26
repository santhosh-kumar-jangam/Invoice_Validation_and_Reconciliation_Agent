# tools/database_tools.py (or your file)
import sqlite3
import json
import traceback 

# It's good practice to have the DB path easily configurable
DATABASE_NAME = r"C:\Users\Yaswanth\Invoice_Validation_and_Reconciliation_Agent\database.db"

def save_bank_transactions_tool(transactions_json_string: str) -> str:
    """
    Saves bank transactions from a JSON string to the SQLite database.
    This function is specifically designed to handle the output of the
    `parse_bank_statement_text` tool.
    """
    print("--- [Tool] Starting database save operation ---")
    try:
        # The input might be a dictionary already if called internally, 
        # or a string if coming from an agent. Handle both.
        if isinstance(transactions_json_string, dict):
            data = transactions_json_string
        else:
            data = json.loads(transactions_json_string)
            
        transactions = data.get("transactions", [])
        if not transactions:
            print("WARNING: No transactions found in the JSON data.")
            return "No transactions found in the provided JSON to save."
        print(f"Found {len(transactions)} transactions to process.")
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: The input string is not valid JSON. Error: {e}")
        return f"Error: Input was not a valid JSON string. Details: {e}"

    conn = None
    inserted_count = 0
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_transactions (
            transaction_id TEXT PRIMARY KEY,
            invoice_number TEXT,
            description TEXT,
            status TEXT,
            transaction_date TEXT,
            debit_amount REAL
        )
        """)

        for i, transaction in enumerate(transactions):
            print(f"\nProcessing transaction #{i+1}: {transaction}")
            try:
                # --- FIX: Directly use the clean data from the parser ---
                # No more cleaning or parsing is needed here.
                
                transaction_id = transaction.get('transaction_id')
                invoice_number = transaction.get('invoice_number')
                description = transaction.get('description')
                transaction_date = transaction.get('transaction_date') # Key is 'transaction_date', not 'date'
                debit_amount = transaction.get('debit_amount')         # Already a float

                # Basic validation: ensure the primary key exists
                if not transaction_id:
                    print(f"  -> SKIPPED: Transaction #{i+1} is missing a 'transaction_id'.")
                    continue

                cursor.execute("""
                    INSERT OR IGNORE INTO bank_transactions (
                        transaction_id, invoice_number, description, status, 
                        transaction_date, debit_amount
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    transaction_id,
                    invoice_number,
                    description,
                    "Cleared",  # Set a default status
                    transaction_date,
                    debit_amount
                ))
                
                if cursor.rowcount > 0:
                    print(f"  -> SUCCESS: Transaction {transaction_id} was inserted.")
                    inserted_count += 1
                else:
                    print(f"  -> IGNORED: Transaction {transaction_id} already exists.")

            except (KeyError, TypeError) as e:
                # This catch block is still useful for unexpected format changes
                print(f"---!!! FAILED ON TRANSACTION #{i+1} !!!---")
                print(f"ERROR DETAILS: {e}")
                print("DATA THAT CAUSED ERROR:", transaction)
                traceback.print_exc()
                return f"Operation failed on a transaction. See server logs for details. Error: {e}"

        print(f"\n--- All transactions processed. Committing {inserted_count} new records. ---")
        conn.commit()
        return f"Success: Saved {inserted_count} new transactions to the database."

    except sqlite3.Error as e:
        print(f"FATAL DATABASE ERROR: {e}")
        traceback.print_exc()
        return f"A fatal database error occurred: {e}"
    finally:
        if conn:
            print("--- Closing database connection. ---")
            conn.close()

def save_invoice_data(invoice_data: dict) -> str:
    """
    Saves extracted invoice data to the 'invoices' table in the database.
    The table schema is relaxed to allow NULL values for better resilience.
    """
    print("--- [Tool] Starting invoice save operation ---")
    
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_number TEXT PRIMARY KEY,
            vendor_name TEXT,
            client_name TEXT,
            invoice_date TEXT,
            due_date TEXT,
            total_amount REAL
        )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO invoices (
                invoice_number, vendor_name, client_name, invoice_date, due_date, total_amount
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            invoice_data.get('invoice_number'),
            invoice_data.get('vendor_name'),
            invoice_data.get('client_name'),
            invoice_data.get('invoice_date'),
            invoice_data.get('due_date'),
            invoice_data.get('total_amount')
        ))

        conn.commit()
        invoice_num = invoice_data.get('invoice_number', 'N/A')
        print(f"  -> SUCCESS: Invoice {invoice_num} was saved to the database.")
        return f"Successfully saved invoice {invoice_num}."

    except sqlite3.Error as e:
        print(f"FATAL DATABASE ERROR saving invoice: {e}")
        traceback.print_exc()
        return f"Error: A database error occurred while saving the invoice: {e}"
    finally:
        if conn:
            conn.close()