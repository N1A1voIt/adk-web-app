from google.adk.agents import LlmAgent
from agent_core.sub_agents.sql_executor_agent.prompt import QUERY_EXECUTION_INSTRUCTION_STR
from agent_core.tools.big_query_execution_tool import query_execution_tool

# LLM Agent for execution of the bigquery sqls
query_execution_agent = LlmAgent(
    name="query_execution_agent",
    model="gemini-2.0-flash-001",
    description=f"This agent is responsible for exeuction of queries in the bigquery and present the result as markdown table",
    instruction=QUERY_EXECUTION_INSTRUCTION_STR,
    tools=[query_execution_tool],
    output_key="query_execution_output"
)
