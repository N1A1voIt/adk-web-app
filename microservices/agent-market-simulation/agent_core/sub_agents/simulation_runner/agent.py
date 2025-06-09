import json
import os

import pandas as pd
from google.adk.agents import LlmAgent

from agent_core.sub_agents.simulation_runner.prompt import SIMULATION_RUNNER_PROMPT
from agent_core.sub_agents.simulation_runner.simulation_tool.monte_carlo import MonteCarloBacktester
from agent_core.tools.big_query_execution_tool import fetch_market_historical_data


def simulate(strategies:str ,lp_output:str):
    data = json.loads(lp_output)
    df = pd.DataFrame(fetch_market_historical_data(PROJECT=os.getenv("BQ_PROJECT_ID"), SYMBOL=data["symbol"]))
    scen_test = {
        "market_volatility": 0.02,
        "market_drift": 0.001,
        "economic_events": ["tech rebound"]
    }
    strategies = strategies.replace("```json","").replace("```","")
    json_strategies = json.loads(strategies)
    backtester = MonteCarloBacktester(df)
    window_size = len(df) // 2
    results = backtester.run_multiple_strategies(json_strategies,scen_test,data["n_simulations"],data["timeframe"],window_size)
    return results

simulation_agent = LlmAgent(
    name = "simulation_agent",
    model = "gemini-2.0-flash-001",
    description = """You are an agent that run a trading simulation""",
    instruction = SIMULATION_RUNNER_PROMPT,
    tools=[simulate],
    output_key = "simulation_output"
)