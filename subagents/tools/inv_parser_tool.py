# subagents/tools/parser.py
import re
from datetime import datetime

def parse_date(date_string: str) -> str | None:
    """Tries to parse a date string from various common formats."""
    if not date_string:
        return None
    date_string = date_string.strip()
    formats_to_try = [
        '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
        '%b %d, %Y', '%B %d, %Y',
        '%d %b %Y', '%d %B %Y'
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_string, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    print(f"Warning: Could not parse date '{date_string}' with known formats.")
    return None

def extract_invoice_data_from_text(text: str) -> dict:
    """
    Extracts invoice details from raw text using precise, label-based regex.
    """
    data = {
        "invoice_number": None, "vendor_name": None, "client_name": None,
        "invoice_date": None, "due_date": None, "total_amount": None,
    }

    patterns = {
        "invoice_number": r"(?i)Invoice Number[:\s]+([A-Z0-9-/]+)",
        "vendor_name":    r"(?i)^Vendor[:\s]+(.*?)\n",
        "client_name":    r"(?i)^Client[:\s]+(.*?)\n",
        "invoice_date":   r"(?i)Invoice Date[:\s]+([\d-]+)",
        "due_date":       r"(?i)Due Date[:\s]+([\d-]+)",
        "total_amount":   r"(?i)Total Amount\s*₹?\s*([\d,]+\.\d{2})",
    }

    for key, pattern in patterns.items():
        
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            raw_value = match.group(1).strip() if match.group(1) else None
            
            if not raw_value:
                continue

            if "date" in key:
                data[key] = parse_date(raw_value)
            elif "amount" in key:
                try:
                    data[key] = float(raw_value.replace(",", ""))
                except ValueError:
                    print(f"Warning: Could not convert amount '{raw_value}' to a number.")
            else:
                data[key] = raw_value.strip()
                
    return data

def parse_bank_statement_text(bank_statement_text: str) -> dict:
    """
    Parses raw text from a bank statement to extract transaction details.

    Args:
        bank_statement_text: The full text content of the bank statement.

    Returns:
        A dictionary structured as {"transactions": [...]}.
    """
    transactions = []
    
    pattern = re.compile(
        r"^(\d{2}-\d{2}-\d{4})\s+"    # 1: Date
        r"(\w+)\s+"                  # 2: Transaction ID
        r"([\w/]+)\s+"               # 3: Invoice Number
        r"(.+?)\s+"                  # 4: Description (non-greedy)
        r"([\d,]+)\s+"               # 5: Debit Amount
        r"([\d,]+)$",                # 6: Balance (we capture it to end the match)
        re.MULTILINE                 # Process line by line
    )

    lines = bank_statement_text.strip().split('\n')
    for line in lines:
        match = pattern.search(line.strip())
        if match:
            # Extract data from the matched groups
            date_str = match.group(1)
            transaction_id = match.group(2)
            invoice_number = match.group(3)
            description = match.group(4)
            debit_str = match.group(5)
            
            # --- Clean and format the extracted data ---
            try:
                # 1. Format date from DD-MM-YYYY to YYYY-MM-DD
                formatted_date = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                
                # 2. Convert debit amount string to a number (float)
                # Note: Your example output showed a string, but a number is more useful.
                # If you absolutely need a string, use str(debit_amount_float)
                debit_amount_float = float(debit_str.replace(",", ""))

                transactions.append({
                    "transaction_id": transaction_id,
                    "invoice_number": invoice_number,
                    "description": description.strip(),
                    "transaction_date": formatted_date,
                    "debit_amount": debit_amount_float 
                })
            except (ValueError, IndexError) as e:
                print(f"Skipping malformed line: '{line}'. Error: {e}")

    return {"transactions": transactions}



