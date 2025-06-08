import numpy as np
import pandas as pd

def compute_ema(series, span): return series.ewm(span=span, adjust=False).mean()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-6)
    return 100 - (100 / (1 + rs))

def compute_bollinger_bands(series, period=20, std=2):
    ma = series.rolling(period).mean()
    std_dev = series.rolling(period).std()
    return ma - std * std_dev, ma + std * std_dev

def compute_indicators(df, strategy):
    if "RSI" in strategy["indicators"]:
        df['RSI'] = compute_rsi(df['Close'], strategy["indicators"]["RSI"]["period"])
    if "EMA" in strategy["indicators"]:
        df['EMA'] = compute_ema(df['Close'], strategy["indicators"]["EMA"]["period"])
    if "EMA_short" in strategy["indicators"]:
        df['EMA_short'] = compute_ema(df['Close'], strategy["indicators"]["EMA_short"]["period"])
    if "EMA_long" in strategy["indicators"]:
        df['EMA_long'] = compute_ema(df['Close'], strategy["indicators"]["EMA_long"]["period"])
    if "Bollinger Bands" in strategy["indicators"]:
        lower, upper = compute_bollinger_bands(df['Close'],
                                               strategy["indicators"]["Bollinger Bands"]["period"],
                                               strategy["indicators"]["Bollinger Bands"]["std"])
        df['lower_bollinger_band'] = lower
        df['upper_bollinger_band'] = upper
    return df
def apply_strategy(df, strategy):
    if "RSI" in strategy["indicators"]:
        df['RSI'] = compute_rsi(df['Close'], strategy["indicators"]["RSI"]["period"])
    if "EMA" in strategy["indicators"]:
        df['EMA'] = compute_ema(df['Close'], strategy["indicators"]["EMA"]["period"])
    if "EMA_short" in strategy["indicators"]:
        df['EMA_short'] = compute_ema(df['Close'], strategy["indicators"]["EMA_short"]["period"])
    if "EMA_long" in strategy["indicators"]:
        df['EMA_long'] = compute_ema(df['Close'], strategy["indicators"]["EMA_long"]["period"])
    if "Bollinger Bands" in strategy["indicators"]:
        lower, upper = compute_bollinger_bands(df['Close'],
                                               strategy["indicators"]["Bollinger Bands"]["period"],
                                               strategy["indicators"]["Bollinger Bands"]["std"])
        df['lower_bollinger_band'] = lower
        df['upper_bollinger_band'] = upper


    df['Signal'] = 0

    if strategy["name"] == "RSI + EMA Crossover":
        df.loc[(df['RSI'] > 50) & (df['Close'] > df['EMA']), 'Signal'] = 1
        df.loc[(df['RSI'] < 50) | (df['Close'] < df['EMA']), 'Signal'] = -1

    elif strategy["name"] == "EMA Crossover":
        df.loc[df['EMA_short'] > df['EMA_long'], 'Signal'] = 1
        df.loc[df['EMA_short'] < df['EMA_long'], 'Signal'] = -1

    elif strategy["name"] == "Bollinger Band Reversion":
        df.loc[df['Close'] < df['lower_bollinger_band'], 'Signal'] = 1
        df.loc[df['Close'] > df['upper_bollinger_band'], 'Signal'] = -1

    
    df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
    df['Daily Return'] = df['Close'].pct_change()
    df['Strategy Return'] = df['Daily Return'] * df['Position'].shift(1)

    return df

def monte_carlo_on_real_data(df_real, strategy, n_simulations=100, window_size=252):
    results = []

    df_full = compute_indicators(df_real.copy(), strategy)

    for _ in range(n_simulations):

        start = np.random.randint(0, len(df_full) - window_size)
        df = df_full.iloc[start:start + window_size].copy()


        df = apply_strategy(df, strategy)

        cum_return = (1 + df['Strategy Return'].dropna()).prod() - 1
        sharpe = df['Strategy Return'].mean() / (df['Strategy Return'].std() + 1e-6) * np.sqrt(252)
        max_dd = ((df['Close'].cummax() - df['Close']) / df['Close'].cummax()).max()

        results.append({
            "Strategy": strategy["name"],
            "Final Return %": round(cum_return * 100, 2),
            "Sharpe Ratio": round(sharpe, 2),
            "Max Drawdown %": round(max_dd * 100, 2)
        })

    return pd.DataFrame(results)