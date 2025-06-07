from agent_core.sub_agents.strategy_agent.market_analyzer.Anlyzer import Analyzer


def fetch_context(SYMBOL:str):
    analyzer = Analyzer(SYMBOL)
    return analyzer.analyze()