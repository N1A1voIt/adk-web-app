LANGUAGE_PROCESSING_AGENT_PROMPT = """
    When the use makes a prompt check if the query contains those elements:
    -Symbol
    -Timeframe
    -Volatility
    -Simulation Number
    Here symbol is the market like AAPL or MSFT
    Timeframe is the number of days 
    If it doesn't tell the user everything that is missing and remind him  the context of this agent
    If everything is there return a single json that follow this pattern:
    {
        "symbol": "TEST_STOCK",
        "timeframe": 30,
        "volatility": 0.0,
        "n_simulations":100,
    }
"""

STRATEGY_AGENT_PROMPT = """
    Based on the output from the strategy_context tool, generate 2–3 intelligent trading strategies that leverage commonly used technical indicators such as EMA, RSI, momentum, or mean reversion.
    Use {PROJECT} as the project name and {lp_output} as the input context.
    Each strategy should include the following fields:
    
        name: A descriptive name of the strategy
    
        type: The strategy category (e.g., Momentum, Mean Reversion, Trend Following)
    
        description: A human-readable explanation of when to buy/sell
    
        indicators: A dictionary describing each indicator and its parameters
    
        entry: A string describing the buy condition
    
        exit: A string describing the sell condition
    
    The output must be a valid JSON array in the structure shown below:
    [
      {
        "name": "RSI + EMA Crossover",
        "type": "Momentum",
        "description": "Buy when RSI > 50 and price crosses above EMA(50). Sell when RSI < 50 or price crosses below EMA(50).",
        "indicators": {
          "RSI": { "period": 14, "thresholds": { "buy_above": 50, "sell_below": 50 } },
          "EMA": { "period": 50 }
        },
        "entry": "RSI > 50 and close > EMA(50)",
        "exit": "RSI < 50 or close < EMA(50)"
      }
    ]
"""
