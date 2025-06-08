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
    The final output should be a json with the following structure:
    [
      {
        "name": "RSI + EMA Crossover",
        "type": "Momentum",
        "description": "Buy when RSI > 50 and price crosses above EMA(50). Sell when RSI < 50 or price crosses below EMA(50).",
        "indicators": {
          "RSI": {"period": 14, "thresholds": {"buy_above": 50, "sell_below": 50}},
          "EMA": {"period": 50}
        },
        "entry": "RSI > 50 and close > EMA(50)",
        "exit": "RSI < 50 or close < EMA(50)"
      }
    ]
"""
