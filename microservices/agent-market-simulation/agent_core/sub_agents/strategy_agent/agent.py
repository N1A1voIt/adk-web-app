from google.adk.agents import LlmAgent

# # LLM Agent for execution of the bigquery sqls
# query_execution_agent = LlmAgent(
#     name="query_execution_agent",
#     model="gemini-2.0-flash-001",
#     description=f"This agent is responsible for exeuction of queries in the bigquery and present the result as markdown table",
#     instruction=QUERY_EXECUTION_INSTRUCTION_STR,
#     tools=[],
#     output_key="query_execution_output"
# )
