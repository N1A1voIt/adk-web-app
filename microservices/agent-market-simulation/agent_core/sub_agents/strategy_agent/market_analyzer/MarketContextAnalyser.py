import pandas as pd
import numpy as np


class MarketContextAnalyzer:
    def __init__(self, df: pd.DataFrame, symbol: str):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if df.empty:
            raise ValueError("DataFrame is empty.")
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain {required_cols}")

        self.df_orig = df.copy()
        self.symbol = symbol
        self.df = self._prepare_data(df.copy())
        self._calculate_indicators()
        self.df.dropna(inplace=True)

    def _prepare_data(self, df):
        df['date_col'] = pd.to_datetime(df['Date'])
        df.sort_values('date_col', inplace=True)
        df.set_index('date_col', inplace=True)
        return df

    def _calculate_indicators(self):
        close = self.df["Close"]
        high = self.df["High"]
        low = self.df["Low"]

        # EMA
        self.df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        self.df["ema_50"] = close.ewm(span=50, adjust=False).mean()

        # RSI
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        avg_gain = up.rolling(14).mean()
        avg_loss = down.rolling(14).mean()
        rs = avg_gain / avg_loss
        self.df["rsi_14"] = 100 - (100 / (1 + rs))

        # MACD
        ema_fast = close.ewm(span=12, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        self.df["macd_line"] = macd_line
        self.df["macd_signal"] = macd_signal
        self.df["macd_hist"] = macd_line - macd_signal

        # ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.df["atr_14"] = tr.rolling(14).mean()

        # Bollinger Bands
        ma = close.rolling(window=20).mean()
        std = close.rolling(window=20).std()
        self.df["bb_upper"] = ma + 2 * std
        self.df["bb_middle"] = ma
        self.df["bb_lower"] = ma - 2 * std

    def analyze(self):
        if self.df.empty:
            return {"Error": "Not enough data to perform analysis after indicator calculation."}

        latest = self.df.iloc[-1]
        previous = self.df.iloc[-2] if len(self.df) > 1 else latest

        current_price = latest["Close"]
        ema_20 = latest["ema_20"]
        ema_50 = latest["ema_50"]
        rsi = latest["rsi_14"]
        atr = latest["atr_14"]
        bb_upper = latest["bb_upper"]
        bb_lower = latest["bb_lower"]
        bb_middle = latest["bb_middle"]
        macd_line = latest["macd_line"]
        macd_signal = latest["macd_signal"]
        macd_hist = latest["macd_hist"]

        # --- Trend ---
        ema_status = "Neutral"
        if ema_20 > ema_50 and previous["ema_20"] <= previous["ema_50"]:
            ema_status = "Bullish Crossover recently occurred"
        elif ema_20 < ema_50 and previous["ema_20"] >= previous["ema_50"]:
            ema_status = "Bearish Crossover recently occurred"
        elif ema_20 > ema_50:
            ema_status = "Bullish (EMA20 > EMA50)"
        elif ema_20 < ema_50:
            ema_status = "Bearish (EMA20 < EMA50)"

        # --- RSI ---
        if pd.isna(rsi):
            rsi_state = "N/A"
        elif rsi > 70:
            rsi_state = "Overbought"
        elif rsi < 30:
            rsi_state = "Oversold"
        elif rsi > 60:
            rsi_state = "Approaching Overbought"
        elif rsi < 40:
            rsi_state = "Approaching Oversold"
        else:
            rsi_state = "Neutral"

        # --- MACD ---
        if pd.isna(macd_line) or pd.isna(macd_signal) or pd.isna(macd_hist):
            macd_state = "N/A"
        elif macd_line > macd_signal and macd_hist > 0:
            macd_state = "Bullish (Line > Signal, Hist Positive)"
        elif macd_line < macd_signal and macd_hist < 0:
            macd_state = "Bearish (Line < Signal, Hist Negative)"
        elif macd_line > macd_signal:
            macd_state = "Potentially Bullish (Line > Signal)"
        elif macd_line < macd_signal:
            macd_state = "Potentially Bearish (Line < Signal)"
        else:
            macd_state = "Neutral"

        # --- ATR ---
        atr_vol_level = "Moderate"
        if current_price > 0:
            atr_pct = (atr / current_price) * 100
            if atr_pct > 2.0:
                atr_vol_level = f"High (~{atr_pct:.1f}%)"
            elif atr_pct < 0.5:
                atr_vol_level = f"Low (~{atr_pct:.1f}%)"
            else:
                atr_vol_level = f"Moderate (~{atr_pct:.1f}%)"
        else:
            atr_vol_level = "N/A"

        # --- Bollinger Band Position ---
        if pd.isna(current_price) or pd.isna(bb_upper) or pd.isna(bb_lower):
            bb_position = "N/A"
        elif current_price > bb_upper:
            bb_position = "Price is above upper band"
        elif current_price < bb_lower:
            bb_position = "Price is below lower band"
        elif current_price > bb_middle + 0.75 * (bb_upper - bb_middle):
            bb_position = "Price is near the upper band"
        elif current_price < bb_middle - 0.75 * (bb_middle - bb_lower):
            bb_position = "Price is near the lower band"
        else:
            bb_position = "Price is within bands (around middle)"

        # --- Support/Resistance ---
        lookback = 20
        resistance = round(self.df["High"].rolling(lookback, min_periods=1).max().iloc[-1], 2)
        support = round(self.df["Low"].rolling(lookback, min_periods=1).min().iloc[-1], 2)

        return {
            "Asset": self.symbol,
            "Current Price": round(current_price, 2),
            "Trend": {
                "20-period EMA": round(ema_20, 2),
                "50-period EMA": f"{round(ema_50, 2)} (Status: {ema_status})",
            },
            "Momentum": {
                "RSI(14)": f"{int(rsi)} ({rsi_state})",
                "MACD(12,26,9)": macd_state,
            },
            "Volatility": {
                "ATR(14)": f"{round(atr, 2)} ({atr_vol_level})",
                "Bollinger Bands(20,2)": f"{bb_position} (U:{round(bb_upper, 2)}, M:{round(bb_middle, 2)}, L:{round(bb_lower, 2)})"
            },
            "Key Levels": {
                f"Resistance (last {lookback} periods)": f"~{resistance}",
                f"Support (last {lookback} periods)": f"~{support}",
            },
            "Recent Patterns": "Pattern detection removed (no pandas_ta or TA-Lib candle functions)"
        }

#
# if __name__ == '__main__':
#     # Create dummy data
#     data_dict = {
#         'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
#                                 '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
#                                 '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
#                                 '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20',
#                                 '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25',
#                                 # Min 25 for EMA50 to be somewhat smooth
#                                 '2023-01-26', '2023-01-27', '2023-01-28', '2023-01-29', '2023-01-30',
#                                 '2023-02-01', '2023-02-02', '2023-02-03', '2023-02-04', '2023-02-05',
#                                 '2023-02-06', '2023-02-07', '2023-02-08', '2023-02-09', '2023-02-10',
#                                 '2023-02-11', '2023-02-12', '2023-02-13', '2023-02-14', '2023-02-15',
#                                 '2023-02-16', '2023-02-17', '2023-02-18', '2023-02-19', '2023-02-20',
#                                 # Needs enough for EMA50
#                                 '2023-02-21', '2023-02-22', '2023-02-23', '2023-02-24', '2023-02-25',
#                                 '2023-02-26', '2023-02-27', '2023-02-28'
#                                 ]),
#         'Open': np.random.uniform(100, 102, size=59),
#         'High': np.random.uniform(102, 105, size=59),
#         'Low': np.random.uniform(98, 100, size=59),
#         'Close': np.random.uniform(100, 103, size=59),
#         'Volume': np.random.randint(1000, 5000, size=59)
#     }
#     # Ensure High is >= Open/Close and Low is <= Open/Close
#     data_dict['High'] = np.maximum(data_dict['High'], data_dict['Open'])
#     data_dict['High'] = np.maximum(data_dict['High'], data_dict['Close'])
#     data_dict['Low'] = np.minimum(data_dict['Low'], data_dict['Open'])
#     data_dict['Low'] = np.minimum(data_dict['Low'], data_dict['Close'])
#
#     sample_df = pd.DataFrame(data_dict)
#
#     try:
#         analyzer = MarketContextAnalyzer(df=sample_df, symbol="TEST_STOCK")
#         context = analyzer.analyze()
#         import json
#
#         print(json.dumps(context, indent=2))
#     except ValueError as e:
#         print(f"Error during analysis: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#
#     print("\n--- Testing with insufficient data (less than longest period for indicators) ---")
#     short_df = sample_df.head(15)  # Less than 20 for BBands/EMA20, much less for EMA50
#     try:
#         analyzer_short = MarketContextAnalyzer(df=short_df, symbol="SHORT_TEST")
#         context_short = analyzer_short.analyze()
#         print(json.dumps(context_short, indent=2))
#     except ValueError as e:
#         print(f"Error with short data: {e}")
#     except Exception as e:
#         print(f"An unexpected error with short data: {e}")