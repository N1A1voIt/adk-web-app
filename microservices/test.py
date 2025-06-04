import numpy as np
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Step 1: Load your stock OHLCV data (assuming CSV with 'Date' and 'Close')
df = pd.read_csv('/home/nyavo/Documents/google-hackathons/adk/stocks/JJA.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

# Step 2: Train Prophet model on Close price
model = Prophet(daily_seasonality=True)
model.fit(df)

# Step 3: Create future dataframe for next 30 days
future = model.make_future_dataframe(periods=70)
forecast = model.predict(future)

# Step 4: Extract predicted mean and uncertainty
predicted = forecast['yhat'].values
predicted_lower = forecast['yhat_lower'].values
predicted_upper = forecast['yhat_upper'].values

# Step 5: Monte Carlo simulation parameters
num_simulations = 100  # Number of simulation paths
forecast_horizon = 70  # Days to simulate after last date
last_date = df['ds'].max()
last_price = df.loc[df['ds'] == last_date, 'y'].values[0]

# Estimate daily returns volatility from historical Close prices
returns = df['y'].pct_change().dropna()
volatility = returns.std()

# Simulate multiple price paths using Geometric Brownian Motion with Prophet forecast trend as drift
simulated_paths = []

for _ in range(num_simulations):
    prices = [last_price]
    for day in range(forecast_horizon):
        # Get Prophet's forecasted price for day t+1
        trend_price = predicted[len(df) + day]
        # Calculate drift as daily return implied by Prophet's trend
        drift = (trend_price - prices[-1]) / prices[-1]

        # Simulate random return with drift + volatility noise
        random_return = np.random.normal(loc=drift, scale=volatility)
        next_price = prices[-1] * (1 + random_return)
        prices.append(next_price)
    simulated_paths.append(prices[1:])  # Skip initial price

# Step 6: Plot only forecasted future + Monte Carlo
plt.figure(figsize=(12, 6))

# Define forecast-only portion
future_forecast = forecast.iloc[len(df):]  # future only

# Plot Prophet forecast mean and uncertainty band
plt.plot(future_forecast['ds'], future_forecast['yhat'], label='Prophet Forecast', color='blue')
plt.fill_between(future_forecast['ds'],
                 future_forecast['yhat_lower'],
                 future_forecast['yhat_upper'],
                 color='blue', alpha=0.2)

# Plot Monte Carlo simulation paths
future_dates = future_forecast['ds']
for sim in simulated_paths:
    plt.plot(future_dates, sim, color='red', alpha=0.1)

# Add zoomed view title and axis labels
plt.title('Zoomed View: Forecast + Monte Carlo Simulation')
plt.xlabel('Date')
plt.ylabel('Predicted Price')
plt.legend()
plt.grid(True)

# Save or show
plt.tight_layout()
plt.savefig("zoomed_forecast_simulation.png")  # Or use plt.show() if interactive
