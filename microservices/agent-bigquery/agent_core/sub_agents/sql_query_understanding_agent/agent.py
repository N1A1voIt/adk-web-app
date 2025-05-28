from google.adk.agents import LlmAgent
from .prompt import QUERY_UNDERSTANDING_PROMPT_STR

query_understanding_agent = LlmAgent(
    name = "query_understanding_agent",
    model = "gemini-2.0-flash-001",
    description = """This agent is responsible for understanding the intent of the user question 
        and identifying tables/columns involved to answer the query
    """,
    instruction = QUERY_UNDERSTANDING_PROMPT_STR,
    output_key = "query_understanding_output"
)
