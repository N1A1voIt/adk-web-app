import json
import sys

import pandas as pd
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from agent_core.sub_agents.strategy_agent.market_analyzer.Anlyzer import Analyzer
from agent_core.sub_agents.strategy_agent.market_analyzer.MarketContextAnalyser import MarketContextAnalyzer
from agent_core.sub_agents.strategy_agent.prompt import STRATEGY_AGENT_PROMPT, LANGUAGE_PROCESSING_AGENT_PROMPT
from agent_core.tools.big_query_execution_tool import fetch_market_historical_data

def strategy_context(PROJECT:str,lp_output:str):
    print(f"before conversion {PROJECT}")
    data = json.loads(lp_output)
    analyzer = Analyzer(symbol=data["symbol"])
    return analyzer.analyze()

language_processing_agent = LlmAgent(
    name = "language_processing_agent",
    model = "gemini-2.0-flash-001",
    description = """You are an agent that fetches structured output from a user request""",
    instruction = LANGUAGE_PROCESSING_AGENT_PROMPT,
    output_key = "lp_output"
)

strategy_agent = LlmAgent(
name = "strategy_agent",
    model = "gemini-2.0-flash-001",
    description = """You are an agent that generate strategy for a trading case.""",
    instruction = STRATEGY_AGENT_PROMPT,
    tools=[strategy_context],
    output_key = "strategy_output"
)