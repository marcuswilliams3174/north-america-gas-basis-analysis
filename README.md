# Natural Gas Market Structure & Trading Signal Model (AECO / Henry Hub)

## Overview

This project builds a systematic analytical framework to evaluate North American natural gas markets, focusing on the relationship between **AECO (Western Canada pricing hub)** and **Henry Hub (US benchmark)**, and how this interacts with storage conditions, seasonal dynamics, and volatility regimes.

The objective is to simulate how a supply & trading desk evaluates **basis behavior, regional pricing dislocations, and directional market bias** in natural gas markets.

---

## Motivation

Natural gas pricing is driven by structural and cyclical forces:

- Regional supply-demand imbalances (AECO vs Henry Hub)
- Storage levels and injection/withdrawal cycles
- Seasonal demand shifts (winter heating vs summer injection)
- Short-term volatility shocks and liquidity constraints

This project translates these dynamics into a structured model for analyzing pricing behavior and generating simple trading signals.

---

## Key Features

### 1. Data Integration
- Henry Hub spot prices
- AECO proxy pricing
- Natural gas storage data
- Fully time-aligned dataset construction

---

### 2. Feature Engineering
- Seasonal classification (Winter vs Summer)
- Basis spread (AECO – Henry Hub)
- Rolling volatility measures
- Storage regime classification
- Spread regime detection (wide / tight / normal)

---

### 3. Market Regime Logic

- **Storage Regime**
  - High storage → bearish pressure
  - Low storage → bullish pressure

- **Seasonality**
  - Winter → demand-driven tightening
  - Summer → injection-driven conditions

- **Basis Regime**
  - Wide spreads → regional constraint / dislocation
  - Tight spreads → normalized conditions

---

### 4. Trading Signal Construction

Signals generated:

- Strong Bullish Bias
- Strong Bearish Bias
- Neutral

Based on:
- Storage conditions
- Seasonal regime
- Basis spread regime

---

### 5. Backtesting Framework

A simplified signal-based evaluation framework:

- Next-period directional returns
- Cumulative PnL tracking
- Strategy performance measurement

---

### 6. Performance Analytics

- Signal hit rate (win rate)
- Seasonal performance breakdown
- Storage regime sensitivity
- Risk-adjusted return proxy (Sharpe-style)
- Strategy edge score

---

## Key Insight

A structural feature of natural gas markets is that:

> Basis dislocations between AECO and Henry Hub tend to widen during periods of storage stress and regional constraint, particularly during seasonal demand transitions.

These conditions often create temporary inefficiencies where pricing deviates from underlying physical fundamentals.

---

## Tools & Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Time-series analysis
- Basic quantitative signal modeling

---

## Project Structure
natural-gas-trading-model/
│
├── data/
├── analysis.py
├── requirements.txt
├── README.md
└── outputs/

---

## How to Run

```bash
pip install -r requirements.txt
python analysis.py
