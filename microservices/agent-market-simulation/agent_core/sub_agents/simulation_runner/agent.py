from google.adk.agents import LlmAgent

from agent_core.sub_agents.simulation_runner.prompt import SIMULATION_RUNNER_PROMPT
from agent_core.sub_agents.simulation_runner.simulation_tool.monte_carlo import MonteCarloBacktester


def simulate(strategies , scenario , df , n_simulations=100):
    backtester = MonteCarloBacktester(df)
    window_size = len(df) // 2
    results = backtester.run_multiple_strategies(strategies,scenario,n_simulations,window_size)
    return results.to_json(orient="records")

simulation_agent = LlmAgent(
    name = "simulation_agent",
    model = "gemini-2.0-flash-001",
    description = """You are an agent that run a trading simulation""",
    instruction = SIMULATION_RUNNER_PROMPT,
    tools=[simulate],
    output_key = "simulation_output"
)