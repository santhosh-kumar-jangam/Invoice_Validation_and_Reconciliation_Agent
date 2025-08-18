from google.adk.agents import LlmAgent
from subagents.prompts.bankstatementparserprompt import prompt

bank_statement_parser_agent = LlmAgent(
    name="BankStatementParserAgent",
    description="Takes raw text from a bank statement and extracts transaction data into a structured JSON format.",
    model="gemini-2.5-flash",
    instruction=prompt
)