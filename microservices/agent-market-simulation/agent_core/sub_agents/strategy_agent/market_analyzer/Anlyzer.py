from agent_core.sub_agents.strategy_agent import market_analyzer
from agent_core.sub_agents.strategy_agent.market_analyzer.MarketContextAnalyser import MarketContextAnalyzer
from agent_core.tools.big_query_execution_tool import fetch_market_historical_data
import os
import pandas as pd
import json


class Analyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol
    def analyze(self) :
        dataset = pd.DataFrame(fetch_market_historical_data(PROJECT=os.getenv("BQ_PROJECT_ID"),SYMBOL=self.symbol))
        analyzer = MarketContextAnalyzer(df=dataset, symbol=self.symbol)
        context = analyzer.analyze()
        print(json.dumps(context, indent=2))
        return context