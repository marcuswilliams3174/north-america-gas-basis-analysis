import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 1. EXTRACT (ROBUST + SAFE)
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

    if best is None:
        raise ValueError(f"Could not extract usable data from {file}")

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

df = hh.merge(aeco, on="Date", how="inner").merge(storage, on="Date", how="inner")
df = df.sort_values("Date").reset_index(drop=True)

# =========================================================
# 5. SAFETY CHECKS
# =========================================================

required = ["HH", "AECO", "Storage"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")


# =========================================================
# 6. FEATURES (STABLE + NO NaN PROPAGATION)
# =========================================================

df["HH_norm"] = (df["HH"] - df["HH"].mean()) / (df["HH"].std() + 1e-9)
df["AECO_norm"] = (df["AECO"] - df["AECO"].mean()) / (df["AECO"].std() + 1e-9)

df["Basis"] = df["AECO_norm"] - df["HH_norm"]

df["HH_ret"] = df["HH"].pct_change().fillna(0)
df["vol"] = df["HH_ret"].rolling(6).std().fillna(df["HH_ret"].std() + 1e-6)

# robust storage z-score
roll_mean = df["Storage"].rolling(12).mean()
roll_std = df["Storage"].rolling(12).std()

df["Storage_Z"] = (df["Storage"] - roll_mean) / (roll_std + 1e-9)
df["Storage_Z"] = df["Storage_Z"].fillna(0)

# seasonality
df["winter"] = df["Date"].dt.month.isin([11,12,1,2,3]).astype(int)


# =========================================================
# 7. SIGNALS (FULLY CLEAN)
# =========================================================

q_high = df["Storage_Z"].quantile(0.8)
q_low = df["Storage_Z"].quantile(0.2)

df["signal"] = 0

df.loc[df["Storage_Z"] <= q_low, "signal"] = 1
df.loc[df["Storage_Z"] >= q_high, "signal"] = -1

# winter adjustment
df["signal"] = df["signal"].astype(float)
df.loc[df["winter"] == 1, "signal"] *= 1.2

# FINAL CLEANING (CRITICAL FIX)
df["signal"] = df["signal"].fillna(0)
df["signal"] = np.sign(df["signal"]).astype(int)


# =========================================================
# 8. RETURNS
# =========================================================

df["position"] = df["signal"] / (df["vol"] + 1e-9)

df["strategy_ret"] = df["position"].shift(1) * df["HH_ret"]
df["strategy_ret"] = df["strategy_ret"].fillna(0)

df["cum_pnl"] = df["strategy_ret"].cumsum()
df["benchmark"] = df["HH_ret"].cumsum()


# =========================================================
# 9. PLOTS (FIXED SCATTER ISSUE)
# =========================================================

plt.figure(figsize=(12,4))
plt.plot(df["Date"], df["cum_pnl"], label="Strategy")
plt.plot(df["Date"], df["benchmark"], label="Buy & Hold")
plt.legend()
plt.title("Strategy vs Benchmark")
plt.show()

plt.figure(figsize=(12,4))
plt.plot(df["Date"], df["Basis"])
plt.title("AECO vs HH Spread")
plt.show()

# SAFE COLOR MAPPING (NO NaNs POSSIBLE)
color_map = {1: "green", -1: "red", 0: "gray"}
colors = df["signal"].astype(int).map(color_map)

plt.figure(figsize=(6,6))
plt.scatter(df["HH_norm"], df["Basis"], c=colors)
plt.title("Regime Map")
plt.show()


# =========================================================
# 10. METRICS
# =========================================================

sharpe = df["strategy_ret"].mean() / (df["strategy_ret"].std() + 1e-9)
total_return = df["cum_pnl"].iloc[-1]

print("\nSharpe:", round(sharpe, 4))
print("Total Return:", round(total_return, 4))
print("Rows:", len(df))
