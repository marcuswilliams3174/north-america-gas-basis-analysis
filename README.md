# Natural Gas Regime-Based Trading Framework  
## AECO vs Henry Hub | Storage & Basis Signal Model  
**Marcus Williams**

---

## Overview

This repository develops a regime-based framework for analyzing North American natural gas markets, focusing on the interaction between **AECO**, **Henry Hub**, and **storage dynamics**.

The model translates physical market conditions into **directional bias and relative value trading signals**, with emphasis on identifying periods of pricing dislocation and regime transition across gas hubs.

---

## Investment Memo (Download)

[Download Natural Gas Market Memo (PDF)](outputs/natural_gas_memo.pdf)

*Note: If the preview does not render, download the file directly for full viewing.*

---

## Core Market Framework

Natural gas pricing is driven by recurring structural imbalances across:

- Storage cycles (tight vs loose conditions)
- Seasonal demand shifts (winter vs summer)
- Regional basis dislocations (AECO vs Henry Hub)
- Volatility regimes linked to physical stress and positioning

This framework maps these drivers into **interpretable trading signals aligned with supply & trading decision-making logic**.

---

## Model Outputs

The framework generates:

- Market regime classification (Bullish / Bearish / Neutral)
- AECO–Henry Hub basis dislocation signal
- Storage-driven directional bias
- Risk-adjusted strategy performance vs benchmark

---

## Key Insight

> Storage stress combined with seasonal transitions is the primary driver of short-term gas price dislocations and basis volatility across North American hubs.

These periods represent conditions where pricing most frequently deviates from underlying physical fundamentals.

---

## Results

### 1. Strategy vs Benchmark (Cumulative Performance)

<img width="980" height="452" alt="Strategy vs Benchmark" src="https://github.com/user-attachments/assets/973e81f4-6d4f-4da4-b7ba-f70c95bc2820" />

Strategy performance is primarily driven by regime timing rather than directional market forecasting. Returns are concentrated during periods of storage-driven imbalance and seasonal transitions where pricing inefficiencies emerge.

---

### 2. AECO vs Henry Hub Basis Dynamics

<img width="980" height="452" alt="AECO vs Henry Hub Basis" src="https://github.com/user-attachments/assets/d871d13f-16a6-47bd-9d69-e7cf761e53b1" />
 
The spread reflects regional dislocations between AECO and Henry Hub. Widening periods indicate supply constraints or transport limitations, while compression reflects balanced market conditions and reduced regional stress.

---

### 3. Regime Classification Map

<img width="612" height="625" alt="Market Regime Map" src="https://github.com/user-attachments/assets/eeb21983-aefc-4b36-b6c7-2a0009ae67e8" />

The regime map shows how storage conditions and market momentum define discrete trading states. Clustering behavior highlights how physical fundamentals translate into repeatable pricing regimes.

---

## Model Logic

The framework integrates:

- Normalized price series
- Storage Z-score signals
- Seasonal classification
- Volatility regime detection
- Basis construction (AECO – Henry Hub)

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Time-series analysis
- Signal-based backtesting

---

## How to Run

```bash
pip install -r requirements.txt
python analysis.py
