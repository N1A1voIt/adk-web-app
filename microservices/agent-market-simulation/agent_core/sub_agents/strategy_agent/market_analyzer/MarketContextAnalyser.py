import pandas as pd
import numpy as np
import pandas_ta as ta  # Make sure you are using pandas_ta


class MarketContextAnalyzer:
    def __init__(self, df: pd.DataFrame, symbol: str):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if df.empty:
            raise ValueError("DataFrame is empty.")
        if not all(col in df.columns for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']):
            raise ValueError("DataFrame must contain 'Date', 'Open', 'High', 'Low', 'Close', 'Volume' columns.")

        self.df_orig = df.copy()  # Keep original if needed
        self.symbol = symbol
        self.df = self._prepare_data(df.copy())
        self._calculate_indicators()
        self.df.dropna(inplace=True)  # Drop NA after all calculations
        if self.df.empty:
            raise ValueError(
                "DataFrame became empty after indicator calculation and NA drop. Check data length and indicator periods.")

    def _prepare_data(self, df_to_prepare: pd.DataFrame) -> pd.DataFrame:
        df_to_prepare['date_col'] = pd.to_datetime(
            df_to_prepare['Date'])  # Use a different name to avoid index name conflict
        df_to_prepare.sort_values("date_col", inplace=True)
        df_to_prepare.set_index("date_col", inplace=True)
        return df_to_prepare

    def _calculate_indicators(self):
        # EMAs
        self.df["ema_20"] = ta.ema(close=self.df["Close"], length=20)  # pandas_ta returns a Series
        self.df["ema_50"] = ta.ema(close=self.df["Close"], length=50)

        # RSI
        self.df["rsi_14"] = ta.rsi(close=self.df["Close"], length=14)  # pandas_ta typically names it with period

        # MACD
        # pandas_ta.macd returns a DataFrame with columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        macd_df = ta.macd(close=self.df["Close"], fast=12, slow=26, signal=9)
        if macd_df is not None and not macd_df.empty:
            self.df["macd_line"] = macd_df.iloc[:, 0]  # Usually the first column is the MACD line
            self.df["macd_signal"] = macd_df.iloc[:, 2]  # Usually the third column is the Signal line
            self.df["macd_hist"] = macd_df.iloc[:, 1]  # Usually the second column is the Histogram
        else:
            self.df["macd_line"] = np.nan
            self.df["macd_signal"] = np.nan
            self.df["macd_hist"] = np.nan

        # ATR
        self.df["atr_14"] = ta.atr(high=self.df["High"], low=self.df["Low"], close=self.df["Close"], length=14)

        # Bollinger Bands
        # pandas_ta.bbands returns a DataFrame with columns like BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
        bb_df = ta.bbands(close=self.df["Close"], length=20, std=2)
        if bb_df is not None and not bb_df.empty:
            self.df["bb_lower"] = bb_df.iloc[:, 0]  # Lower band
            self.df["bb_middle"] = bb_df.iloc[:, 1]  # Middle band
            self.df["bb_upper"] = bb_df.iloc[:, 2]  # Upper band
        else:
            self.df["bb_lower"] = np.nan
            self.df["bb_middle"] = np.nan
            self.df["bb_upper"] = np.nan

    def analyze(self):
        if self.df.empty:
            return {"Error": "Not enough data to perform analysis after indicator calculation."}

        latest = self.df.iloc[-1]
        previous = self.df.iloc[-2] if len(self.df) > 1 else latest  # Handle short dataframes

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

        # --- Determine trend status ---
        ema_status = "Neutral"
        if len(self.df) > 1:  # Need at least 2 points to check crossover
            prev_ema_20 = previous["ema_20"]
            prev_ema_50 = previous["ema_50"]
            if ema_20 > ema_50 and prev_ema_20 <= prev_ema_50:
                ema_status = "Bullish Crossover recently occurred"
            elif ema_20 < ema_50 and prev_ema_20 >= prev_ema_50:
                ema_status = "Bearish Crossover recently occurred"
            elif ema_20 > ema_50:
                ema_status = "Bullish (EMA20 > EMA50)"
            elif ema_20 < ema_50:
                ema_status = "Bearish (EMA20 < EMA50)"
        elif not pd.isna(ema_20) and not pd.isna(ema_50):  # Only one point of data after NA drop
            if ema_20 > ema_50:
                ema_status = "Bullish (EMA20 > EMA50)"
            elif ema_20 < ema_50:
                ema_status = "Bearish (EMA20 < EMA50)"

        # --- Determine RSI state ---
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

        # --- Determine MACD state ---
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

        # --- ATR Volatility Level (Example) ---
        atr_vol_level = "Moderate"
        if not pd.isna(atr) and not pd.isna(current_price) and current_price > 0:
            atr_pct_of_price = (atr / current_price) * 100
            if atr_pct_of_price > 2.0:
                atr_vol_level = f"High (~{atr_pct_of_price:.1f}%)"
            elif atr_pct_of_price < 0.5:
                atr_vol_level = f"Low (~{atr_pct_of_price:.1f}%)"
            else:
                atr_vol_level = f"Moderate (~{atr_pct_of_price:.1f}%)"
        else:
            atr_vol_level = "N/A"

        # --- Bollinger Band position ---
        if pd.isna(current_price) or pd.isna(bb_upper) or pd.isna(bb_lower):
            bb_position = "N/A"
        elif current_price > bb_upper:
            bb_position = "Price is above upper band"
        elif current_price < bb_lower:
            bb_position = "Price is below lower band"
        # More refined "near" logic:
        elif current_price > bb_middle + 0.75 * (bb_upper - bb_middle):
            bb_position = "Price is near the upper band"
        elif current_price < bb_middle - 0.75 * (bb_middle - bb_lower):
            bb_position = "Price is near the lower band"
        else:
            bb_position = "Price is within bands (around middle)"

        # --- Key levels (N-period high/low) ---
        lookback_key_levels = 20  # e.g., last 20 periods
        resistance = round(self.df["High"].rolling(window=lookback_key_levels, min_periods=1).max().iloc[-1],
                           2) if not self.df.empty else "N/A"
        support = round(self.df["Low"].rolling(window=lookback_key_levels, min_periods=1).min().iloc[-1],
                        2) if not self.df.empty else "N/A"

        # --- Recent Patterns (Placeholder - enhance with ta.cdl_*) ---
        # Example: Check for Doji on the PREVIOUS bar
        recent_patterns_text = "None significant detected (or not checked)."
        if len(self.df) > 1:
            doji_series = ta.cdl_doji(open_=self.df['Open'], high=self.df['High'], low=self.df['Low'],
                                      close=self.df['Close'])
            if doji_series is not None and not pd.isna(doji_series.iloc[-2]) and doji_series.iloc[
                -2] != 0:  # pandas_ta returns 100 for Doji
                recent_patterns_text = f"Doji detected on {self.df.index[-2].date()}"

        return {
            "Asset": self.symbol,
            "Current Price": round(current_price, 2) if not pd.isna(current_price) else "N/A",
            "Trend": {
                "20-period EMA": round(ema_20, 2) if not pd.isna(ema_20) else "N/A",
                "50-period EMA": f"{round(ema_50, 2) if not pd.isna(ema_50) else 'N/A'} (Status: {ema_status})",
            },
            "Momentum": {
                "RSI(14)": f"{int(rsi) if not pd.isna(rsi) else 'N/A'} ({rsi_state})",
                "MACD(12,26,9)": macd_state,
            },
            "Volatility": {
                "ATR(14)": f"{round(atr, 2) if not pd.isna(atr) else 'N/A'} ({atr_vol_level})",
                f"Bollinger Bands({20},{2})": f"{bb_position} (U:{round(bb_upper, 2) if not pd.isna(bb_upper) else 'N/A'}, M:{round(bb_middle, 2) if not pd.isna(bb_middle) else 'N/A'}, L:{round(bb_lower, 2) if not pd.isna(bb_lower) else 'N/A'})",
            },
            "Key Levels": {
                f"Resistance (last {lookback_key_levels} periods)": f"~{resistance}",
                f"Support (last {lookback_key_levels} periods)": f"~{support}",
            },
            "Recent Patterns": recent_patterns_text
        }


if __name__ == '__main__':
    # Create dummy data
    data_dict = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                                '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20',
                                '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25',
                                # Min 25 for EMA50 to be somewhat smooth
                                '2023-01-26', '2023-01-27', '2023-01-28', '2023-01-29', '2023-01-30',
                                '2023-02-01', '2023-02-02', '2023-02-03', '2023-02-04', '2023-02-05',
                                '2023-02-06', '2023-02-07', '2023-02-08', '2023-02-09', '2023-02-10',
                                '2023-02-11', '2023-02-12', '2023-02-13', '2023-02-14', '2023-02-15',
                                '2023-02-16', '2023-02-17', '2023-02-18', '2023-02-19', '2023-02-20',
                                # Needs enough for EMA50
                                '2023-02-21', '2023-02-22', '2023-02-23', '2023-02-24', '2023-02-25',
                                '2023-02-26', '2023-02-27', '2023-02-28'
                                ]),
        'Open': np.random.uniform(100, 102, size=59),
        'High': np.random.uniform(102, 105, size=59),
        'Low': np.random.uniform(98, 100, size=59),
        'Close': np.random.uniform(100, 103, size=59),
        'Volume': np.random.randint(1000, 5000, size=59)
    }
    # Ensure High is >= Open/Close and Low is <= Open/Close
    data_dict['High'] = np.maximum(data_dict['High'], data_dict['Open'])
    data_dict['High'] = np.maximum(data_dict['High'], data_dict['Close'])
    data_dict['Low'] = np.minimum(data_dict['Low'], data_dict['Open'])
    data_dict['Low'] = np.minimum(data_dict['Low'], data_dict['Close'])

    sample_df = pd.DataFrame(data_dict)

    try:
        analyzer = MarketContextAnalyzer(df=sample_df, symbol="TEST_STOCK")
        context = analyzer.analyze()
        import json

        print(json.dumps(context, indent=2))
    except ValueError as e:
        print(f"Error during analysis: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\n--- Testing with insufficient data (less than longest period for indicators) ---")
    short_df = sample_df.head(15)  # Less than 20 for BBands/EMA20, much less for EMA50
    try:
        analyzer_short = MarketContextAnalyzer(df=short_df, symbol="SHORT_TEST")
        context_short = analyzer_short.analyze()
        print(json.dumps(context_short, indent=2))
    except ValueError as e:
        print(f"Error with short data: {e}")
    except Exception as e:
        print(f"An unexpected error with short data: {e}")