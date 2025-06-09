import numpy as np
import pandas as pd

class MonteCarloBacktester:
    def __init__(self, df):
        self.df_real = df.copy()

    def compute_ema(self, series, span):
        return series.ewm(span=span, adjust=False).mean()

    def compute_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-6)
        return 100 - (100 / (1 + rs))

    def compute_bollinger_bands(self, series, period=20, std=2):
        ma = series.rolling(period).mean()
        std_dev = series.rolling(period).std()
        return ma - std * std_dev, ma + std * std_dev

    def compute_indicators(self, df, strategy):
        if "RSI" in strategy["indicators"]:
            df['RSI'] = self.compute_rsi(df['Close'], strategy["indicators"]["RSI"]["period"])
        if "EMA" in strategy["indicators"]:
            df['EMA'] = self.compute_ema(df['Close'], strategy["indicators"]["EMA"]["period"])
        if "EMA_short" in strategy["indicators"]:
            df['EMA_short'] = self.compute_ema(df['Close'], strategy["indicators"]["EMA_short"]["period"])
        if "EMA_long" in strategy["indicators"]:
            df['EMA_long'] = self.compute_ema(df['Close'], strategy["indicators"]["EMA_long"]["period"])
        if "Bollinger Bands" in strategy["indicators"]:
            lower, upper = self.compute_bollinger_bands(
                df['Close'],
                strategy["indicators"]["Bollinger Bands"]["period"],
                strategy["indicators"]["Bollinger Bands"]["std"]
            )
            df['lower_bollinger_band'] = lower
            df['upper_bollinger_band'] = upper
        return df

    def apply_strategy(self, df, strategy):
        df = self.compute_indicators(df.copy(), strategy)
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

    def apply_scenario(self, df, scenario):
        df = df.copy()
        df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
        np.random.seed(42)
        noise = np.random.normal(
            loc=scenario.get("market_drift", 0),
            scale=scenario.get("market_volatility", 0.01),
            size=len(df)
        )
        df['simulated_log_return'] = df['log_return'].fillna(0) + noise
        df['Simulated Close'] = df['Close'].iloc[0] * np.exp(np.cumsum(df['simulated_log_return']))
        df['Close'] = df['Simulated Close']
        return df

    def run_simulation(self, strategy, scenario=None, n_simulations=100, window_size=252):
        results = []
        df_base = self.apply_scenario(self.df_real, scenario) if scenario else self.df_real.copy()
        df_full = self.compute_indicators(df_base.copy(), strategy)

        for _ in range(n_simulations):
            start = np.random.randint(0, len(df_full) - window_size)
            df = df_full.iloc[start:start + window_size].copy()
            df = self.apply_strategy(df, strategy)

            cum_return = (1 + df['Strategy Return'].dropna()).prod() - 1
            sharpe = df['Strategy Return'].mean() / (df['Strategy Return'].std() + 1e-6) * np.sqrt(252)
            max_dd = ((df['Close'].cummax() - df['Close']) / df['Close'].cummax()).max()

            results.append({
                "Scenario": scenario.get("economic_events", ["None"])[0] if scenario else "None",
                "Strategy": strategy["name"],
                "Final Return %": round(cum_return * 100, 2),
                "Sharpe Ratio": round(sharpe, 2),
                "Max Drawdown %": round(max_dd * 100, 2)
            })

        return pd.DataFrame(results)

    def monte_carlo_future_simulation(self, strategy, scenario=None, n_simulations=100, context_days=252, n_days=30):
        results = []

        df_context = self.df_real.copy().iloc[-context_days:].copy()
        df_context = self.compute_indicators(df_context, strategy)

        for _ in range(n_simulations):
            last_price = df_context['Close'].iloc[-1]
            noise = np.random.normal(
                loc=scenario.get("market_drift", 0) if scenario else 0,
                scale=scenario.get("market_volatility", 0.01) if scenario else 0.01,
                size=n_days
            )
            future_log_returns = noise
            future_prices = last_price * np.exp(np.cumsum(future_log_returns))

            df_future = pd.DataFrame({
                "Close": future_prices
            })

            df_future = self.compute_indicators(df_future, strategy)
            df_future = self.apply_strategy(df_future, strategy)

            cum_return = (1 + df_future['Strategy Return'].dropna()).prod() - 1
            sharpe = df_future['Strategy Return'].mean() / (df_future['Strategy Return'].std() + 1e-6) * np.sqrt(252)
            max_dd = ((df_future['Close'].cummax() - df_future['Close']) / df_future['Close'].cummax()).max()

            results.append({
                "Scenario": scenario.get("economic_events", ["None"])[0] if scenario else "None",
                "Strategy": strategy["name"],
                "Predicted Return %": round(cum_return * 100, 2),
                "Sharpe Ratio": round(sharpe, 2),
                "Max Drawdown %": round(max_dd * 100, 2)
            })

        return pd.DataFrame(results)

    def summarize_results(self, results_df):
        return {
            "Strategy":results_df["Strategy"].iloc[0],
            "average_final_return": f"{results_df['Predicted Return %'].mean():.2f}%",
            "average_sharpe_ratio": round(results_df['Sharpe Ratio'].mean(), 2),
            "average_max_drawdown": f"{results_df['Max Drawdown %'].mean():.2f}%"
        }

    def run_multiple_strategies(self, strategies, scenario=None,next_days = 30, n_simulations=100, window_size=252):
        summaries = []
        for strategy in strategies:
            results = self.monte_carlo_future_simulation(strategy, scenario, n_simulations, window_size,next_days)
            summaries.append(self.summarize_results(results))
        return summaries
