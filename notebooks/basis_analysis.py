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

df = df.dropna().reset_index(drop=True)

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
# STORAGE REGIME (SMOOTHED)
# -----------------------------

storage_ma = df["Storage"].rolling(52).mean()

df["Storage_Regime"] = np.where(
    df["Storage"] > storage_ma,
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
# BACKTEST (NO LOOKAHEAD BIAS)
# -----------------------------

signal = np.where(
    df["Trade_Signal"] == "Strong Bullish Bias",
    1,
    np.where(df["Trade_Signal"] == "Strong Bearish Bias", -1, 0)
)

df["signal_return"] = df["price_change"].shift(-1) * signal

df["cumulative_pnl"] = df["signal_return"].cumsum()

# -----------------------------
# PERFORMANCE ANALYTICS
# -----------------------------

results = df.dropna(subset=["signal_return"]).copy()

results["Correct_Direction"] = np.where(
    ((results["Trade_Signal"] == "Strong Bullish Bias") & (results["price_change"] > 0)) |
    ((results["Trade_Signal"] == "Strong Bearish Bias") & (results["price_change"] < 0)),
    1,
    0
)

win_rate = results["Correct_Direction"].mean()

print("\n--- SIGNAL PERFORMANCE ---")
print(f"Win Rate: {win_rate:.2%}")

regime_perf = results.groupby("Season")["signal_return"].mean()
print("\n--- SEASONAL PERFORMANCE ---")
print(regime_perf)

storage_perf = results.groupby("Storage_Regime")["signal_return"].mean()
print("\n--- STORAGE PERFORMANCE ---")
print(storage_perf)

mean_return = results["signal_return"].mean()
std_return = results["signal_return"].std()

sharpe_proxy = mean_return / std_return if std_return != 0 else 0

print("\n--- SHARPE PROXY ---")
print(sharpe_proxy)

edge_score = win_rate * sharpe_proxy

print("\n--- EDGE SCORE ---")
print(edge_score)

# -----------------------------
# HERO IMAGE (BASIS)
# -----------------------------

plt.figure(figsize=(12,6))

plt.plot(df["Date"], df["Basis"], label="AECO - Henry Hub Basis")
plt.axhline(df["Basis"].mean(), linestyle="--", label="Mean")

plt.title("AECO vs Henry Hub Basis Dislocation")
plt.xlabel("Date")
plt.ylabel("Basis Spread")

plt.legend()
plt.tight_layout()

plt.savefig("../outputs/hero_basis_chart.png", dpi=300)
plt.close()

# -----------------------------
# CUMULATIVE PNL
# -----------------------------

plt.figure(figsize=(12,6))

plt.plot(df["Date"], df["cumulative_pnl"])

plt.title("Natural Gas Strategy Backtest")
plt.xlabel("Date")
plt.ylabel("Cumulative PnL")

plt.tight_layout()

plt.savefig("../outputs/cumulative_pnl.png", dpi=300)
plt.close()

# -----------------------------
# REGIME SCATTER
# -----------------------------

color_map = {
    "Strong Bullish Bias": "green",
    "Strong Bearish Bias": "red",
    "Neutral": "gray"
}

colors = df["Trade_Signal"].map(color_map)

plt.figure(figsize=(8,6))

plt.scatter(df["HenryHub"], df["Basis"], c=colors)

plt.title("Gas Market Regime Classification")
plt.xlabel("Henry Hub")
plt.ylabel("Basis")

plt.tight_layout()

plt.savefig("../outputs/regime_scatter.png", dpi=300)
plt.close()

print("\n✅ Charts exported to /outputs folder")
