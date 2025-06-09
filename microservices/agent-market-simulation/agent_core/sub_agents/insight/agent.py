from google.adk.agents import LlmAgent

from agent_core.sub_agents.insight.prompt import INSIGHT_PROMPT

insight_agent = LlmAgent(
    name="insight_agent",
    model="gemini-2.0-flash-001",
    description="""You are an agent that gives insight to an user""",
    instruction=INSIGHT_PROMPT,
    output_key="insight_output"
)