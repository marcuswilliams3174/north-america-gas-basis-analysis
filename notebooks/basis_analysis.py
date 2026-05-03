import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# GLOBAL STYLE (TRADING DESK LOOK)
# =========================================================

plt.style.use("dark_background")

def style_axis(ax, title):
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2)
    for spine in ax.spines.values():
        spine.set_alpha(0.3)

# =========================================================
# 1. ROBUST EXTRACTOR
# =========================================================

def extract(file, label):
    xls = pd.ExcelFile(file)

    best = None
    best_score = -1

    for sheet in xls.sheet_names:
        raw = pd.read_excel(file, sheet_name=sheet)
        raw.columns = [str(c).lower().strip() for c in raw.columns]

        for c in raw.columns:
            dates = pd.to_datetime(raw[c], errors="coerce")
            if dates.notna().sum() < 10:
                continue

            for v in raw.columns:
                if v == c:
                    continue

                vals = pd.to_numeric(
                    raw[v].astype(str).str.replace(r"[^0-9\.\-]", "", regex=True),
                    errors="coerce"
                )

                temp = pd.DataFrame({"Date": dates, label: vals}).dropna()

                if len(temp) > best_score:
                    best = temp
                    best_score = len(temp)

    return best.sort_values("Date")


# =========================================================
# 2. LOAD DATA
# =========================================================

hh = extract("henry_hub_price.xls", "HH")
storage = extract("gas_storage.xls", "Storage")

aeco = pd.read_csv("aeco_proxy.csv")
aeco.columns = ["Date", "AECO"]
aeco["Date"] = pd.to_datetime(aeco["Date"])
aeco["AECO"] = pd.to_numeric(aeco["AECO"], errors="coerce")
aeco = aeco.dropna()


# =========================================================
# 3. MONTHLY ALIGNMENT
# =========================================================

def monthly(df):
    df["Date"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    return df.groupby("Date").mean().reset_index()

hh = monthly(hh)
storage = monthly(storage)
aeco = monthly(aeco)


# =========================================================
# 4. MERGE
# =========================================================

df = hh.merge(aeco, on="Date").merge(storage, on="Date")
df = df.sort_values("Date").reset_index(drop=True)


# =========================================================
# 5. FEATURES
# =========================================================

# Normalized prices
df["HH_norm"] = (df["HH"] - df["HH"].mean()) / df["HH"].std()
df["AECO_norm"] = (df["AECO"] - df["AECO"].mean()) / df["AECO"].std()

# Basis
df["Basis"] = df["AECO_norm"] - df["HH_norm"]

# Returns
df["HH_ret"] = df["HH"].pct_change().fillna(0)

# Volatility (annualized-ish)
df["vol"] = df["HH_ret"].rolling(6).std().clip(lower=0.02)

# Storage Z-score (rolling)
df["Storage_Z"] = (
    (df["Storage"] - df["Storage"].rolling(12).mean()) /
    (df["Storage"].rolling(12).std() + 1e-6)
).fillna(0)

# Seasonality
df["winter"] = df["Date"].dt.month.isin([11,12,1,2,3]).astype(int)


# =========================================================
# 6. SIGNALS (INSTITUTIONAL STYLE)
# =========================================================

q_high = df["Storage_Z"].quantile(0.8)
q_low = df["Storage_Z"].quantile(0.2)

df["signal"] = 0
df.loc[df["Storage_Z"] <= q_low, "signal"] = 1
df.loc[df["Storage_Z"] >= q_high, "signal"] = -1

# seasonal tilt
df["signal"] = df["signal"] * (1 + 0.2 * df["winter"])
df["signal"] = df["signal"].fillna(0)


# =========================================================
# 7. POSITION SIZING (REALISTIC)
# =========================================================

df["position"] = df["signal"] / (df["vol"] + 1e-6)

# cap leverage (CRITICAL)
df["position"] = df["position"].clip(-5, 5)


# =========================================================
# 8. RETURNS
# =========================================================

df["strategy_ret"] = df["position"].shift(1) * df["HH_ret"]
df["strategy_ret"] = df["strategy_ret"].fillna(0)

df["cum_pnl"] = df["strategy_ret"].cumsum()
df["benchmark"] = df["HH_ret"].cumsum()


# =========================================================
# 9. PERFORMANCE METRICS
# =========================================================

def sharpe(x):
    return x.mean() / (x.std() + 1e-6)

def max_dd(x):
    cum = x.cumsum()
    return (cum - cum.cummax()).min()

print("\nSharpe:", round(sharpe(df["strategy_ret"]), 3))
print("Max Drawdown:", round(max_dd(df["strategy_ret"]), 3))
print("Final Return:", round(df["cum_pnl"].iloc[-1], 3))


# =========================================================
# 10. CHART 1 — STRATEGY VS BENCHMARK
# =========================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(df["Date"], df["cum_pnl"], linewidth=2, label="Strategy")
ax.plot(df["Date"], df["benchmark"], linestyle="--", label="Benchmark")

style_axis(ax, "Strategy vs Benchmark (Cumulative Returns)")
ax.legend()

plt.show()


# =========================================================
# 11. CHART 2 — BASIS SPREAD
# =========================================================

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(df["Date"], df["Basis"], linewidth=2)
ax.axhline(0, linestyle="--", alpha=0.5)

style_axis(ax, "AECO vs Henry Hub Basis (Normalized Spread)")

plt.show()


# =========================================================
# 12. CHART 3 — REGIME MAP
# =========================================================

# HARD FIX for your crash
colors = df["signal"].map({1:"green", -1:"red", 0:"gray"})
colors = colors.fillna("gray")

fig, ax = plt.subplots(figsize=(7,7))

ax.scatter(
    df["HH_norm"],
    df["Basis"],
    c=colors,
    alpha=0.7
)

style_axis(ax, "Market Regime Map (Storage-Driven Signals)")

ax.set_xlabel("Henry Hub (Normalized)")
ax.set_ylabel("Basis (AECO - HH)")

plt.show()
