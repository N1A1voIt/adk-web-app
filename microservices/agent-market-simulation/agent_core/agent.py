from google.adk.agents import BaseAgent, LlmAgent


class MarketSimulatorAgent(BaseAgent):
    strategy_planner_agent : LlmAgent
