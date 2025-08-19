# tools/database_tools.py (or your file)
import sqlite3
import json
from datetime import datetime
import traceback 

DATABASE_NAME = "C:\\Users\\Yaswanth\\Invoice_Validation_and_Reconciliation_Agent\\database.db"

def save_bank_transactions_tool(transactions_json_string: str) -> str:
    """
    Parses, cleans, and saves bank transactions to the database.
    This version includes detailed diagnostic logging.
    """
    print("--- Starting database save operation ---")
    try:
        data = json.loads(transactions_json_string)
        transactions = data.get("transactions", [])
        if not transactions:
            print("WARNING: No transactions found in the JSON data.")
            return "No transactions found in the provided JSON to save."
        print(f"Found {len(transactions)} transactions to process.")
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: The input string is not valid JSON. Error: {e}")
        return "Error: Input was not a valid JSON string."

    conn = None
    inserted_count = 0
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        for i, transaction in enumerate(transactions):
            print(f"\nProcessing transaction #{i+1}: {transaction}")
            try:
                debit_amount_str = transaction.get('debit_amount', '0').replace(',', '')
                debit_amount_float = float(debit_amount_str)

                date_obj = datetime.strptime(transaction['date'], '%d-%m-%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
                
                description = transaction.get('description') 

                cursor.execute("""
                    INSERT OR IGNORE INTO bank_transactions (
                        transaction_id, invoice_number, description, status, 
                        transaction_date, debit_amount
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    transaction['transaction_id'],
                    transaction['invoice_number'],
                    description,
                    "Cleared",
                    formatted_date,
                    debit_amount_float
                ))
                
                if cursor.rowcount > 0:
                    print(f"  -> SUCCESS: Transaction {transaction['transaction_id']} was inserted.")
                    inserted_count += 1
                else:
                    print(f"  -> IGNORED: Transaction {transaction['transaction_id']} already exists.")

            except (KeyError, ValueError, TypeError) as e:
                # THIS IS THE MOST IMPORTANT PART
                print(f"---!!! FAILED ON TRANSACTION #{i+1} !!!---")
                print(f"ERROR TYPE: {type(e).__name__}")
                print(f"ERROR DETAILS: {e}")
                print("DATA THAT CAUSED ERROR:", transaction)
                traceback.print_exc() # Prints the full stack trace
                # We will stop the whole process on the first error to make it obvious
                return f"Operation failed on a transaction. See server logs for details. Error: {e}"

        print("\n--- All transactions processed. Committing to database. ---")
        conn.commit()
        return f"Successfully inserted {inserted_count} new transactions into the database."

    except sqlite3.Error as e:
        print(f"FATAL DATABASE ERROR: {e}")
        traceback.print_exc()
        return f"A fatal database error occurred: {e}"
    finally:
        if conn:
            print("--- Closing database connection. ---")
            conn.close()