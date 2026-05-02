import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# LOAD DATA
# -----------------------------

hh = pd.read_excel("../data/henry_hub_price.xls")
storage = pd.read_excel("../data/gas_storage.xls")
aeco = pd.read_csv("../data/aeco_proxy.csv")

# -----------------------------
# CLEAN HENRY HUB
# -----------------------------

hh = hh.dropna()
hh.columns = ["Date", "HenryHub"]
hh["Date"] = pd.to_datetime(hh["Date"])
hh = hh.sort_values("Date")

# -----------------------------
# CLEAN STORAGE
# -----------------------------

storage = storage.dropna()
storage = storage.iloc[:, :2]
storage.columns = ["Date", "Storage"]
storage["Date"] = pd.to_datetime(storage["Date"])
storage = storage.sort_values("Date")

# -----------------------------
# CLEAN AECO
# -----------------------------

aeco["Date"] = pd.to_datetime(aeco["Date"])
aeco = aeco.sort_values("Date")

# -----------------------------
# MERGE ALL DATA (TIME-ALIGNED)
# -----------------------------

df = pd.merge(hh, aeco, on="Date", how="inner")
df = pd.merge(df, storage, on="Date", how="inner")

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------

df["Month"] = df["Date"].dt.month

df["Season"] = np.where(
    df["Month"].isin([11, 12, 1, 2, 3]),
    "Winter",
    "Summer"
)

df["Basis"] = df["AECO"] - df["HenryHub"]

df["price_change"] = df["HenryHub"].pct_change()

df["volatility"] = df["price_change"].rolling(4).std()

vol_threshold = df["volatility"].mean() + df["volatility"].std()

df["Volatility_Event"] = df["volatility"] > vol_threshold

# -----------------------------
# SPREAD REGIMES
# -----------------------------

basis_mean = df["Basis"].mean()
basis_std = df["Basis"].std()

df["Spread_Regime"] = np.where(
    df["Basis"] > basis_mean + basis_std,
    "Wide Spread",
    np.where(
        df["Basis"] < basis_mean - basis_std,
        "Tight Spread",
        "Normal"
    )
)

# -----------------------------
# STORAGE REGIME (DYNAMIC)
# -----------------------------

storage_mean = df["Storage"].rolling(52).mean()

df["Storage_Regime"] = np.where(
    df["Storage"] > storage_mean,
    "High Storage (Bearish)",
    "Low Storage (Bullish)"
)

# -----------------------------
# TRADING SIGNAL
# -----------------------------

df["Trade_Signal"] = np.where(
    (df["Storage_Regime"] == "Low Storage (Bullish)") &
    (df["Season"] == "Winter") &
    (df["Spread_Regime"] == "Wide Spread"),
    "Strong Bullish Bias",

    np.where(
        (df["Storage_Regime"] == "High Storage (Bearish)") &
        (df["Season"] == "Summer") &
        (df["Spread_Regime"] == "Tight Spread"),
        "Strong Bearish Bias",
        "Neutral"
    )
)

# -----------------------------
# BACKTEST (SIMPLE SIGNAL MODEL)
# -----------------------------

df["signal_return"] = df["price_change"] * np.where(
    df["Trade_Signal"] == "Strong Bullish Bias",
    1,
    np.where(df["Trade_Signal"] == "Strong Bearish Bias", -1, 0)
)

df["cumulative_pnl"] = df["signal_return"].cumsum()

# -----------------------------
# PLOTS
# -----------------------------

# 1. STRATEGY PERFORMANCE
plt.figure()
plt.plot(df["Date"], df["cumulative_pnl"])
plt.title("Natural Gas Strategy Backtest (Simple Model)")
plt.xlabel("Date")
plt.ylabel("Cumulative PnL")
plt.show()

# 2. PRICES
plt.figure()
plt.plot(df["Date"], df["HenryHub"], label="Henry Hub")
plt.plot(df["Date"], df["AECO"], label="AECO")
plt.legend()
plt.title("North American Gas Prices")
plt.show()

# 3. BASIS
plt.figure()
plt.plot(df["Date"], df["Basis"])
plt.axhline(0)
plt.title("AECO - Henry Hub Basis Spread")
plt.show()

# 4. PRICE VS BASIS
plt.figure()
plt.scatter(df["HenryHub"], df["Basis"])
plt.title("Price vs Basis Relationship")
plt.xlabel("Henry Hub")
plt.ylabel("Basis")
plt.show()

# 5. REGIME SIGNALS
color_map = {
    "Strong Bullish Bias": "green",
    "Strong Bearish Bias": "red",
    "Neutral": "gray"
}

colors = df["Trade_Signal"].map(color_map)

plt.figure()
plt.scatter(df["HenryHub"], df["Basis"], c=colors)
plt.title("Gas Market Regime Signals")
plt.xlabel("Henry Hub")
plt.ylabel("Basis")
plt.show()
