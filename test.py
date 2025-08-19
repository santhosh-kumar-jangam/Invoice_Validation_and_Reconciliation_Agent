# test_db.py
from subagents.tools.database_tools import save_bank_transactions_tool # Assumes the function is in database_tools.py

print("--- RUNNING STANDALONE DATABASE TEST ---")

# SCENARIO 1: A PERFECTLY VALID JSON STRING
print("\n--- [TEST 1: Valid Data] ---")
valid_json_data = """
{
    "transactions": [
        {
            "date": "25-12-2025",
            "transaction_id": "TXN-VALID-001",
            "invoice_number": "INV-VALID-001",
            "debit_amount": "1,500.50",
            "description": "Payment for valid invoice"
        },
        {
            "date": "26-12-2025",
            "transaction_id": "TXN-VALID-002",
            "invoice_number": "INV-VALID-002",
            "debit_amount": "3000",
            "description": "Another valid payment"
        }
    ]
}
"""
result1 = save_bank_transactions_tool(valid_json_data)
print(f"\nRESULT 1: {result1}")
print("---------------------------------")


# SCENARIO 2: A JSON STRING WITH A BAD DATE FORMAT
print("\n--- [TEST 2: Invalid Date] ---")
invalid_date_json = """
{
    "transactions": [
        {
            "date": "2025-12-27",  # WRONG FORMAT! Should be DD-MM-YYYY
            "transaction_id": "TXN-BAD-DATE-001",
            "invoice_number": "INV-BAD-DATE-001",
            "debit_amount": "100.00",
            "description": "This will fail"
        }
    ]
}
"""
result2 = save_bank_transactions_tool(invalid_date_json)
print(f"\nRESULT 2: {result2}")
print("---------------------------------")