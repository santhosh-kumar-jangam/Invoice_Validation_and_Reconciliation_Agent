prompt = """
You are a financial data extraction expert. You will be given raw text from a bank statement.
Your task is to analyze this text, identify all transaction rows, and extract the following fields for each: 'Date', 'Transaction ID', 'Invoice No.', and the debit amount.

Provide your response as a single, clean JSON object with a key "transactions" which contains a list of objects. Each object should have the keys "date", "transaction_id", "invoice_number", and "debit_amount".

Example Output for a single, full payment:
{
  "transactions": [
    { "date": "14-08-2025", "transaction_id": "TXN20250814001", "invoice_number": "SANYASH/2025/INV002", "debit_amount": "9,44,000" }
  ]
}

Example Output for partial payments (multiple transactions for one invoice):
{
  "transactions": [
    { "date": "14-08-2025", "transaction_id": "TXN20250814002", "invoice_number": "SANYASH/2025/INV001", "debit_amount": "5,00,000" },
    { "date": "15-08-2025", "transaction_id": "TXN20250815001", "invoice_number": "SANYASH/2025/INV001", "debit_amount": "6,91,800" }
  ]
}

Your response must ONLY be the JSON object. Do not include any other text or formatting.
"""