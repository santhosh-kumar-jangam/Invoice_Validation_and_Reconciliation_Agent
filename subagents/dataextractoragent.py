from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from subagents.datanormalizeragent import data_normalizer_agent
from subagents.prompts.dataextractorprompt import prompt
from subagents.tools.dataextractortool import list_gcs_invoices, extract_invoice_content, upload_json_to_gcs

data_extractor_agent = LlmAgent(
    name="DataExtractorAgent",
    description="Accesses the invoices from the cloud and extracts the info into a json object",
    model="gemini-2.0-flash",
    instruction=prompt,
    tools=[list_gcs_invoices, extract_invoice_content, AgentTool(agent=data_normalizer_agent), upload_json_to_gcs]
)