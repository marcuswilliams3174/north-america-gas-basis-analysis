import pandas as pd
import matplotlib.pyplot as plt

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

# -----------------------------
# CLEAN AECO
# -----------------------------

aeco["Date"] = pd.to_datetime(aeco["Date"])

# -----------------------------
# MERGE ALL DATA
# -----------------------------

df = pd.merge(hh, aeco, on="Date", how="inner")

# -----------------------------
# CALCULATE BASIS
# -----------------------------

df["Basis"] = df["AECO"] - df["HenryHub"]

# -----------------------------
# PLOTS
# -----------------------------

# 1. Henry Hub vs AECO
plt.figure()
plt.plot(df["Date"], df["HenryHub"], label="Henry Hub")
plt.plot(df["Date"], df["AECO"], label="AECO")
plt.legend()
plt.title("North American Gas Prices")
plt.show()

# 2. BASIS SPREAD
plt.figure()
plt.plot(df["Date"], df["Basis"])
plt.title("AECO - Henry Hub Basis Spread")
plt.axhline(0)
plt.show()

# 3. SIMPLE RELATIONSHIP VIEW
plt.figure()
plt.scatter(df["HenryHub"], df["Basis"])
plt.title("Price vs Basis Relationship")
plt.xlabel("Henry Hub Price")
plt.ylabel("Basis (AECO - HH)")
plt.show()
