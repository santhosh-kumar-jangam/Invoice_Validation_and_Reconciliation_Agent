from google.adk.agents import LlmAgent
from subagents.prompts.datanormalizerprompt import prompt

data_normalizer_agent = LlmAgent(
    name="DataNormalizerAgent",
    description="Normalizes the invoice info into a json object",
    model="gemini-2.0-flash",
    instruction=prompt
)