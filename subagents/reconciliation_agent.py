# subagents/reconciliationagent.py
from google.adk.agents import LlmAgent 
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
# Import the new, simple tools
from subagents.tools.reconciliation_tools import get_all_invoice_jsons, extract_text_from_bank_statement
from subagents.tools.emailsendertool import send_email
# Import the agent this agent will use as a tool
from subagents.bankstatementparseragent import bank_statement_parser_agent
from subagents.prompts.reconciliationprompt import prompt


reconciliation_agent = LlmAgent(
    name="ReconciliationAgent",
    description="Manages the final reconciliation step: gathering data, using a parser agent, and generating the final report and at last send final report to email.",
    model=LiteLlm("openai/gpt-4o"), 
    instruction=prompt,
    tools=[
        get_all_invoice_jsons,
        extract_text_from_bank_statement,
        send_email,
        AgentTool(agent=bank_statement_parser_agent)
        
    ]
    
)