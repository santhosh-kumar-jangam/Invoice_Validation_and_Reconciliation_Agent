from google.adk.agents import LlmAgent
from subagents.prompts.bankstatementparserprompt import prompt
from subagents.tools.database_tools import save_bank_transactions_tool

bank_statement_parser_agent = LlmAgent(
    name="BankStatementParserAgent",
    description="Takes raw text from a bank statement and extracts transaction data into a structured JSON format.",
    model="gemini-2.0-flash",
    instruction=prompt,
    tools=[save_bank_transactions_tool]

)