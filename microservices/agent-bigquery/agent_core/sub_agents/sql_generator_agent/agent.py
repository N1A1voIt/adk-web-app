from google.adk.agents import LlmAgent
from agent_core.tools.metadata_extraction_tool import bigquery_metdata_extraction_tool
from .prompt import QUERY_GENERATION_INSTRUCTION_STR
# from tools.metadata_extraction_tool import bigquery_metdata_extraction_tool
# LLM Agent for generation of bigquery based on the analysis received from the query_understanding_agent
query_generation_agent = LlmAgent(
    name="query_generation_agent",
    model="gemini-2.0-flash-001",
    description="This agent is responsible for generating bigquery queries in standard sql dialect",
    instruction=QUERY_GENERATION_INSTRUCTION_STR,
    tools=[bigquery_metdata_extraction_tool],
    output_key="query_generation_output"
)