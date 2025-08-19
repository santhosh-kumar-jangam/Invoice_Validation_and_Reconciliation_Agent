import sqlite3
 
with sqlite3.connect("database.db") as conn:
    cursor = conn.cursor()
 
    cursor.execute("drop table reconciliation_results;")
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS reconciliation_results (
                run_id VARCHAR(36) NOT NULL,
                invoice_number VARCHAR(255) NOT NULL,
                vendor_name VARCHAR(255) NOT NULL,
                claimed_total DECIMAL(14, 2) NOT NULL,
                payment_dates TEXT,
                transaction_ids TEXT,
                amount_paid DECIMAL(14, 2),
                status VARCHAR(50) NOT NULL CHECK (status IN ('PAID', 'DUE')),
                verdict VARCHAR(50) NOT NULL CHECK (verdict IN ('VERIFIED', 'UNDERPAID', 'OVERPAID', 'UNPAID', 'DISPUTED')),
                conclusion TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (run_id, invoice_number)
            );
        """)
 
    conn.commit()