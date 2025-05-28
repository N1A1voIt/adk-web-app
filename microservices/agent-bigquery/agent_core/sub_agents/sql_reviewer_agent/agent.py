from google.adk.agents import LlmAgent
from agent_core.sub_agents.sql_reviewer_agent.prompt import QUERY_REVIEW_REWRITE_INSTRUCTION_STR

query_review_rewrite_agent = LlmAgent(
    name="query_review_agent",
    model="gemini-2.0-flash-001",
    description=f"This agent is responsible for reviewing queries in the bigquery",
    instruction=QUERY_REVIEW_REWRITE_INSTRUCTION_STR,
    output_key="query_review_rewrite_output"
)