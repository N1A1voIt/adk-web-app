import asyncio

from google.adk import Runner
from google.adk.agents import BaseAgent, LlmAgent
from typing import AsyncGenerator

from google.adk.sessions import InMemorySessionService
from google.genai import types
from typing_extensions import override
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext

import logging

from agent_core.sub_agents.insight.agent import insight_agent
from agent_core.sub_agents.simulation_runner.agent import simulation_agent
# from agent_core.sub_agents.scenarioagent.agent import scenario_agent
from agent_core.sub_agents.strategy_agent.agent import language_processing_agent, strategy_agent
from agent_core.tools.init_state import initialize_state_var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
APP_NAME = "parallel_research_app"
USER_ID = "research_user_01"
SESSION_ID = "parallel_research_session"
GEMINI_MODEL = "gemini-2.0-flash"
class MarketSimulatorAgent(BaseAgent):
    language_processing_agent:LlmAgent
    strategy_agent:LlmAgent
    simulation_agent:LlmAgent
    insight_agent:LlmAgent
    def __init__(self,
                     name: str,
                     language_processing_agent:LlmAgent,
                     strategy_agent:LlmAgent,
                     simulation_agent: LlmAgent,
                     insight_agent:LlmAgent
                 ):
        super().__init__(
            name=name,
            language_processing_agent=language_processing_agent,
            strategy_agent=strategy_agent,
            simulation_agent=simulation_agent,
            insight_agent=insight_agent,
            before_agent_callback=initialize_state_var,
            description="This is a Orchestrator Agent which executes the simulation workflows using the sub_agents provided"
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] - "+ ctx.session.state['PROJECT'])
        async for event in self.language_processing_agent.run_async(ctx):
            logger.info(f"[{self.name}] - {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        lp_output = ""
        if "lp_output" in ctx.session.state:
            lp_output = ctx.session.state['lp_output']
            logger.info(f"[{self.name}] - {lp_output}")

        if lp_output is None or "```json" not in lp_output:
            return
        ctx.session.state['lp_output'] = ctx.session.state['lp_output'].replace("```json", "").replace("```","")

        async for event in self.strategy_agent.run_async(ctx):
            logger.info(f"[{self.name}] - {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        strategy_output = ""
        if "strategy_output" in ctx.session.state:
            strategy_output = ctx.session.state['strategy_output']
            logger.info(f"[{self.name}] - {strategy_output}")

        if strategy_output is None or "```json" not in strategy_output:
            return

        async for event in self.simulation_agent.run_async(ctx):
            logger.info(f"[{self.name}] - {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        simulation_output = ""
        if "simulation_output" in ctx.session.state:
            simulation_output = ctx.session.state['simulation_output']
            logger.info(f"[{self.name}] - {simulation_output}")

        if simulation_output is None or "```json" not in simulation_output:
            return

        async for event in self.insight_agent.run_async(ctx):
            logger.info(f"[{self.name}] - {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        insight_output = ""
        if "insight_output" in ctx.session.state:
            insight_output = ctx.session.state['insight_output']
            logger.info(f"[{self.name}] - {insight_output}")

        if insight_output is None or "```json" not in insight_output:
            return



        # ctx.session.state['output'] = "Hello World"

market_simulator_agent = MarketSimulatorAgent(name="Agent",language_processing_agent=language_processing_agent,strategy_agent=strategy_agent,simulation_agent=simulation_agent,insight_agent=insight_agent)
root_agent = market_simulator_agent
#
#
# session_service = InMemorySessionService()
# session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))
# runner = Runner(agent=market_simulator_agent, app_name=APP_NAME, session_service=session_service)
#
#
# # Agent Interaction
# def call_agent(query):
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
#
#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("Agent Response: ", final_response)