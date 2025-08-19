from google.adk.agents import LlmAgent

from subagents.dataextractoragent import data_extractor_agent
from subagents.invoicevalidatoragent import invoice_validation_agent
from subagents.reconciliation_agent import reconciliation_agent
from rootagent.rootprompt import prompt

root_agent = LlmAgent(
    name="ReconciliationPipeline",
    description="Agent that runs an automated invoice reconciliation pipeline",
    model="gemini-2.5-flash",
    instruction=prompt,
    sub_agents=[
        data_extractor_agent,
        invoice_validation_agent,
        reconciliation_agent
    ]
)