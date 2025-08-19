# rootagent/agent.py

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# --- Import your specialized sub-agent INSTANCES ---
# These agents must be defined in their respective files as you've shown.
from subagents.dataextractoragent import data_extractor_agent
from subagents.reconciliation_agent import reconciliation_agent

# --- Define the prompt that will guide the orchestrator ---
# This instruction is the "brain" of the orchestrator. It tells the LLM
# how to use its tools (the other agents) in the correct sequence.
# rootagent/agent.py

# ... (imports) ...

prompt = """
You are a master workflow orchestrator. Your job is to execute a two-step sequence.

1.  First, call the `DataExtractorAgent`. Give it a simple command like "start". Wait for it to confirm it has finished.
2.  Second, after the `DataExtractorAgent` is done, call the `ReconciliationAgent`. Give it a simple command like "start".

The final answer from the `ReconciliationAgent` is the final answer for the entire workflow.


"""

# --- Define the list of tools the orchestrator can use ---
# Here, the tools are the other agents, wrapped in AgentTool.
orchestrator_tools = [
    AgentTool(agent=data_extractor_agent),
    AgentTool(agent=reconciliation_agent),
]

# --- Create the orchestrator agent ---
# We use a ReactAgent because it needs to reason and use tools.
# This single instance is what the ADK framework will run.
root_agent = Agent(
    name="OrchestratorAgent",
    description="Manages the end-to-end invoice processing and reconciliation workflow.",
    model="gemini-2.5-flash",
    instruction=prompt,
    tools=orchestrator_tools,
    
)

from subagents.reconciliation_agent import reconciliation_agent

# --- Define the prompt that will guide the orchestrator ---
# This instruction is the "brain" of the orchestrator. It tells the LLM
# how to use its tools (the other agents) in the correct sequence.
# rootagent/agent.py

# ... (imports) ...

prompt = """
You are a master workflow orchestrator. Your job is to execute a two-step sequence.

1.  First, call the `DataExtractorAgent`. Give it a simple command like "start". Wait for it to confirm it has finished.
2.  Second, after the `DataExtractorAgent` is done, call the `ReconciliationAgent`. Give it a simple command like "start".

The final answer from the `ReconciliationAgent` is the final answer for the entire workflow.


"""

# --- Define the list of tools the orchestrator can use ---
# Here, the tools are the other agents, wrapped in AgentTool.
orchestrator_tools = [
    AgentTool(agent=data_extractor_agent),
    AgentTool(agent=reconciliation_agent),
]

# --- Create the orchestrator agent ---
# We use a ReactAgent because it needs to reason and use tools.
# This single instance is what the ADK framework will run.
root_agent = Agent(
    name="OrchestratorAgent",
    description="Manages the end-to-end invoice processing and reconciliation workflow.",
    model="gemini-2.5-flash",
    instruction=prompt,
    tools=orchestrator_tools,
    
)