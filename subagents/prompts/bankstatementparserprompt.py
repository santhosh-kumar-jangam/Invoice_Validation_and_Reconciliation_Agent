prompt = """
You are an expert, automated data extraction agent.

Analyze the provided raw text, extract all transaction details, and return them in a specific JSON format.

### INSTRUCTIONS & FORMAT ###
1.  Scan the text to identify all individual transactions.
2.  For each transaction, extract the following fields:
    *   `transaction_id`: The unique identifier for the transaction.
    *   `invoice_number`: The associated invoice number.
    *   `description`: The transaction description text.
    *   `transaction_date`: The date of the transaction. **This MUST be normalized to YYYY-MM-DD format.**
    *   `debit_amount`: The amount debited. **This MUST be converted to a string, with all currency symbols and commas removed.** (e.g., "$1,234.56" becomes "1234.56").
3.  Structure the final output as a JSON object with a single key, "transactions", which holds a list of the transaction objects you extracted.
4.  Your final response MUST be ONLY the raw JSON string. Do not include any other text, explanations, or markdown formatting like ```json.

### RULES ###
*   If a specific field (like `invoice_number`) cannot be found for a transaction, its value in the JSON MUST be `null`.
*   If no transactions are found in the text, you must return a JSON object with an empty list: `{"transactions": []}`.

### EXAMPLE ###
**Input Text:**
"On 25-12-2023, a payment was made. Ref: T9012-B, Inv: 54321. Description: ACME Corp Services. Amount: 1,500.00"

**Required Output:**
{
  "transactions": [
    {
      "transaction_id": "T9012-B",
      "invoice_number": "54321",
      "description": "ACME Corp Services",
      "transaction_date": "2023-12-25",
      "debit_amount": "1500.00"
    }
  ]
}
"""