import pdfplumber
import os
from subagents.tools.inv_parser_tool import extract_invoice_data_from_text

# --- IMPORTANT ---
# Set the path to your local PDF file here
PDF_FILE_PATH = r"C:\Users\Yaswanth\Downloads\invoice1.pdf"

def main():
    """
    A simple script to extract text from a local PDF and test the parser.
    """
    if not os.path.exists(PDF_FILE_PATH):
        print(f"Error: The file was not found at '{PDF_FILE_PATH}'")
        print("Please update the PDF_FILE_PATH variable in this script.")
        return

    print("--- 1. EXTRACTING RAW TEXT FROM PDF ---")
    full_text = ""
    with pdfplumber.open(PDF_FILE_PATH) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    raw_text = full_text.strip()
    print("-------------------- RAW TEXT START --------------------")
    print(raw_text)
    print("--------------------- RAW TEXT END ---------------------")

    print("\n--- 2. PARSING EXTRACTED TEXT ---")
    extracted_data = extract_invoice_data_from_text(raw_text)

    print("\n--- 3. PARSED DATA RESULT ---")
    import json
    print(json.dumps(extracted_data, indent=2))


if __name__ == "__main__":
    main()