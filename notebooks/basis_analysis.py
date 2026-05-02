import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA
# -----------------------------

price = pd.read_excel("../data/henry_hub_price.xls")
storage = pd.read_excel("../data/gas_storage.xls")

# -----------------------------
# CLEAN PRICE DATA
# -----------------------------

price = price.dropna()

# Rename columns (EIA format fix)
price.columns = ["Date", "Price"]

price["Date"] = pd.to_datetime(price["Date"])

# Sort by date
price = price.sort_values("Date")

# -----------------------------
# CLEAN STORAGE DATA
# -----------------------------

storage = storage.dropna()

# Take first 2 columns only (date + storage)
storage = storage.iloc[:, :2]
storage.columns = ["Date", "Storage"]

storage["Date"] = pd.to_datetime(storage["Date"])

# -----------------------------
# MERGE DATASETS
# -----------------------------

df = pd.merge(price, storage, on="Date", how="inner")

# -----------------------------
# DERIVED METRICS
# -----------------------------

df["price_change"] = df["Price"].pct_change()

df["storage_change"] = df["Storage"].pct_change()

# -----------------------------
# PLOTS
# -----------------------------

# 1. Price
plt.figure()
plt.plot(df["Date"], df["Price"])
plt.title("Henry Hub Natural Gas Price")
plt.xlabel("Date")
plt.ylabel("Price ($/MMBtu)")
plt.show()

# 2. Storage
plt.figure()
plt.plot(df["Date"], df["Storage"])
plt.title("US Natural Gas Storage Levels")
plt.xlabel("Date")
plt.ylabel("Billion Cubic Feet")
plt.show()

# 3. Relationship (VERY IMPORTANT FOR TRADING)
plt.figure()
plt.scatter(df["Storage"], df["Price"])
plt.title("Storage vs Gas Price Relationship")
plt.xlabel("Storage")
plt.ylabel("Price")
plt.show()
