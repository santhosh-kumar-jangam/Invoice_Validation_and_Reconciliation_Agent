import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

from jinja2 import Template

load_dotenv()

html_template_str = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background-color: #f5f7fa;
    margin: 0; padding: 20px;
    color: #333;
  }
  .container {
    max-width: 800px;
    margin: auto;
    background-color: #ffffff;
    padding: 30px 40px;
    border-radius: 8px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
  }
  h1 {
    color: #2c5282;
    font-size: 26px;
    margin-bottom: 20px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 10px;
  }
  h2 {
    color: #2c5282;
    font-size: 20px;
    margin-top: 25px;
    margin-bottom: 10px;
  }
  .section {
    margin-bottom: 20px;
    padding: 15px 20px;
    border-left: 4px solid #3182ce;
    background: #f8fafc;
    border-radius: 6px;
  }
  .highlight {
    background: #edf2f7;
    padding: 8px 12px;
    border-radius: 6px;
    font-family: Consolas, monospace;
    font-size: 14px;
    margin: 6px 0;
    color: #2d3748;
  }
  .status {
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 8px;
    font-size: 14px;
  }
  .status.paid {
    background-color: #c6f6d5;
    color: #22543d;
  }
  .status.due {
    background-color: #fed7d7;
    color: #742a2a;
  }
  .status.unpaid {
    background-color: #feb2b2;
    color: #742a2a;
  }
  p.footer {
    font-size: 12px;
    color: #a0aec0;
    margin-top: 40px;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    padding-top: 12px;
    font-style: italic;
  }
</style>
</head>
<body>
  <div class="container">
    <h1>Invoice Validation Report</h1>

    {% for report in reports %}
    <h2>Reconciliation Audit – Invoice: {{ report.invoice_number }}</h2>

    <div class="section">
      <b>Case Overview:</b>

      Vendor: {{ report.vendor_name }}

      Invoice Number: <span class="highlight">{{ report.invoice_number }}
</span>
      Claimed Total: {{ report.claimed_total }}
    </div>

    <div class="section">
      <b>Investigation Findings:</b>
      <div class="highlight">
        Payment Date: {{ report.payment_date }}

        Transaction ID: {{ report.transaction_id }}

        Amount Paid: {{ report.amount_paid }}
      </div>
    </div>

    <div class="section">
      <b>Conclusion & Verdict:</b>

      <span class="status {{ report.status|lower }}">
        {{ report.status | upper }} - {{ report.verdict }}
      
</span>
      {{ report.conclusion }}
    </div>
    {% endfor %}

    <p class="footer">© {{ year }} All rights reserved.</p>
  </div>
</body>
</html>
"""

def send_email(subject: str, reports:list[dict] ) -> dict:
    """
    Sends a professional HTML email with invoice reconciliation results,
    rendered dynamically into a styled HTML template.

    Args:
        subject (str): Subject line of the email.
        reports (list[dict]): A list of reconciliation results, where each dict contains:
            - invoice_number (str): Unique invoice identifier.
            - vendor_name (str): Name of the vendor issuing the invoice.
            - claimed_total (str or float): Total amount claimed on the invoice.
            - payment_date (str): Date of the matched payment transaction.
            - transaction_id (str): Unique identifier/reference from the bank statement.
            - amount_paid (str or float): Amount paid for the invoice.
            - status (str): Payment status (e.g., "paid", "due", "underpaid").
            - verdict (str): Short verdict text (e.g., "Verified", "Mismatch").
            - conclusion (str): Detailed explanation of reconciliation result.
    Returns:
        dict: A dictionary indicating success or failure with a status message.
    """
    sender_email = "swetha26072002@gmail.com"
    password = "dsrnyzgfdgylpywx"
    receiver_email = "santoshbablu3@gmail.com"
    
    # Render HTML template with injected body content
    template = Template(html_template_str)
    html_body = template.render(reports=reports, year=datetime.now().year)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        return {"status": "Email sent successfully"}
    except Exception as e:
        return {"status": f"Error: {e}"}
    finally:
        server.quit()

if __name__ == "__main__":
    send_email(subject="test", reports=
    [
    {
        "invoice_number": "SANYASH/2025/INV002",
        "vendor_name": "Vertex Industrial Solutions",
        "claimed_total": "944000",
        "payment_date": "14-08-2025",
        "transaction_id": "TXN20250814001",
        "amount_paid": "800000",
        "status": "DUE",
        "verdict": "UNPAID",
        "conclusion": "The amount paid (944000) matches the invoice total. This invoice is fully reconciled."
    }])