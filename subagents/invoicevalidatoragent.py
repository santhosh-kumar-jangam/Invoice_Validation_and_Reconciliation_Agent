from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from subagents.rulesconsultantagent import rules_consultant_agent
from subagents.prompts.invoicevalidatorprompt import prompt
from subagents.tools.dataextractortool import list_json_invoices, fetch_json_invoice
from subagents.tools.emailsendertool import send_violation_email

invoice_validation_agent = LlmAgent(
    name="InvoiceValidationAgent",
    description="Validates invoice JSONs using rules from the internal rules document.",
    model="gemini-2.5-flash",
    instruction=prompt,
    tools=[
        list_json_invoices,
        fetch_json_invoice,
        AgentTool(agent=rules_consultant_agent),
        send_violation_email
    ]
)