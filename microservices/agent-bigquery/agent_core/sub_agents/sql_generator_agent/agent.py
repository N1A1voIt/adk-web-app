from google.adk.agents import LlmAgent
from prompt import QUERY_GENERATION_INSTRUCTION_STR
from tools.metadata_extraction_tool import bigquery_metdata_extraction_tool

# LLM Agent for generation of bigquery based on the analysis received from the query_understanding_agent
query_generation_agent = LlmAgent(
    name="query_generation_agent",
    model="gemini-2.5-flash-preview-04-17",
    description="This agent is responsible for generating bigquery queries in standard sql dialect",
    instruction=QUERY_GENERATION_INSTRUCTION_STR,
    tools=[bigquery_metdata_extraction_tool],
    output_key="query_generation_output"
)

# Agent Prompt pasted here for easy reference
QUERY_GENERATION_INSTRUCTION_STR = """
    You are playing role of bigquery sql writer.
    Your job is write bigquery sqls in standard dialect.

    - Use the analysis done by the query understanding agent as below
      {query_understanding_output}
    - Use the project as {PROJECT}, location as {BQ_LOCATION}, dataset as {DATASET} for generating the bigquery queries for the user provided question.
    - Use the `bigquery_metadata_extraction_tool` for metadata extraction for understanding the tables, columns, datatypes and description of the columns.
    Output only the generated query as text
    """