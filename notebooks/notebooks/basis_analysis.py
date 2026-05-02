import pandas as pd
import matplotlib.pyplot as plt

# Load data (placeholder structure for now)
# You will replace with real EIA / yfinance data

data = pd.DataFrame({
    "date": pd.date_range(start="2023-01-01", periods=100),
    "henry_hub": range(100),
    "aeco_proxy": range(100, 200)
})

# Calculate basis
data["basis"] = data["aeco_proxy"] - data["henry_hub"]

# Plot basis
plt.figure()
plt.plot(data["date"], data["basis"])
plt.title("AECO vs Henry Hub Basis (Proxy Model)")
plt.show()
