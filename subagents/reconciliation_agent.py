# subagents/reconciliationagent.py
from google.adk.agents import LlmAgent 
from google.adk.models.lite_llm import LiteLlm
# Import the new, simple tools
from subagents.tools.reconciliation_tools import get_all_invoice_jsons, extract_text_from_bank_statement,parse_bank_statement_text
from subagents.tools.emailsendertool import send_email
from subagents.prompts.reconciliationprompt import prompt


reconciliation_agent = LlmAgent(
    name="ReconciliationAgent",
    description="Manages the final reconciliation step: gathering data, parsing the data and generating the final report and at last send final report to email.",
    model=LiteLlm("openai/gpt-4o"), 
    instruction=prompt,
    tools=[
        get_all_invoice_jsons,
        extract_text_from_bank_statement,
        send_email,
        parse_bank_statement_text
        
    ]
    
)