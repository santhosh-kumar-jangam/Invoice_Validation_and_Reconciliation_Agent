# # rootagent/agent.py

# from google.adk.agents import Agent
# from google.adk.tools.agent_tool import AgentTool

# # --- Import your specialized sub-agent INSTANCES ---
# # These agents must be defined in their respective files as you've shown.
# from subagents.dataextractoragent import data_extractor_agent
from subagents.reconciliation_agent import reconciliation_agent
# from subagents.invoicevalidatoragent import invoice_validation_agent



# # In your root_agent.py

# prompt = """
# You are a master workflow orchestrator. Your job is to execute a multi-step sequence. The final output of the entire workflow is either the result from the ReconciliationAgent or the failure report from the InvoiceValidationAgent.

# 1. First, call the `DataExtractorAgent`. Give it a simple command like "start" and wait for its confirmation.

# 2. Second, call the `InvoiceValidationAgent`. Give it a simple command like "start" and carefully inspect its final response.
#     - If the agent's final response is "Validation successful. All invoices passed." OR "Validation successful. No invoices to process.", then you must proceed to the next step.
#     - If the agent's final response is anything else (it will be a detailed report), then the entire workflow has failed. **You must stop all further actions. Do not call any more tools. Conclude your work by providing the complete, unmodified failure report you received in the `Final Answer:` section of your response.**

# 3. Third, ONLY if the validation agent succeeded, call the `ReconciliationAgent`. Give it a simple command like "start". The final answer from this agent is the final answer for the entire workflow.

# Remember, the workflow MUST end in one of two ways: a successful report from the ReconciliationAgent, or a failure report from the InvoiceValidationAgent.
# """

# # --- Define the list of tools the orchestrator can use ---
# # Here, the tools are the other agents, wrapped in AgentTool.
# orchestrator_tools = [
#     AgentTool(agent=data_extractor_agent),
#     AgentTool(agent=reconciliation_agent),
#     AgentTool(agent=invoice_validation_agent)
# ]

# # --- Create the orchestrator agent ---
# # We use a ReactAgent because it needs to reason and use tools.
# # This single instance is what the ADK framework will run.
# root_agent = Agent(
#     name="OrchestratorAgent",
#     description="Manages the end-to-end invoice processing,validating rules and reconciliation workflow.",
#     model="gemini-2.0-flash",
#     instruction=prompt,
#     tools=orchestrator_tools,
    
# )

root_agent=reconciliation_agent