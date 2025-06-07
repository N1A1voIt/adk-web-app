LANGUAGE_PROCESSING_AGENT_PROMPT = """
    When the use makes a prompt check if the query contains those elements:
    -Symbol
    -Timeframe
    -Volatility
    Here symbol is the market like AAPL or MSFT
    Timeframe is the number of days 
    If it doesn't tell the user everything that is missing and remind him  the context of this agent
    If everything is there return a single json that follow this pattern:
    {
        "symbol": "TEST_STOCK",
        "timeframe": "30",
        "volatility": 0.0
    }
"""

STRATEGY_AGENT_PROMPT = """
    Generates 2–3 smart strategies (e.g., EMA, RSI, momentum, mean reversion).
    You will generate those strategies based on the strategy_context tool output.
    Use {PROJECT} as the Project and {lp_output} as the LP output.
"""
