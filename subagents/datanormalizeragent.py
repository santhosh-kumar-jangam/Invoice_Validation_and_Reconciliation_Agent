from google.adk.agents import LlmAgent
from subagents.prompts.datanormalizerprompt import prompt
from google.adk.models.lite_llm import LiteLlm

data_normalizer_agent = LlmAgent(
    name="DataNormalizerAgent",
    description="Normalizes the invoice info into a json object",
    model=LiteLlm("openai/gpt-4o"),
    instruction=prompt
)