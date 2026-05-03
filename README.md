Natural Gas Regime-Based Trading Framework
AECO vs Henry Hub | Storage & Basis Signal Model
Overview

This repository builds a regime-based framework for analyzing North American natural gas markets using AECO, Henry Hub, and storage data.

The model translates physical market conditions into directional and relative value trading signals.

Core Idea

Natural gas pricing is driven by recurring structural imbalances across:

Storage cycles (tight vs loose conditions)
Seasonal demand shifts (winter vs summer)
Regional basis dislocations (AECO vs Henry Hub)
Volatility regimes linked to physical stress

This framework maps these drivers into interpretable trading signals.

Model Outputs
Market regime classification (Bullish / Bearish / Neutral)
AECO–Henry Hub basis dislocation signal
Storage-driven directional bias
Simple backtested performance vs buy-and-hold
Key Insight

Storage stress combined with seasonal transitions is the primary driver of short-term gas price dislocations and basis volatility across North American hubs.

Outputs
Strategy vs Benchmark performance
AECO–HH basis dynamics
Regime classification map

(See /outputs folder for charts)

Tech Stack

Python | Pandas | NumPy | Matplotlib | Time Series Analysis

How to Run
pip install -r requirements.txt
python analysis.py
