# GTA VI Launch-Day Twitch Viewers Forecaster

[![make.fun](https://img.shields.io/badge/make.fun-gta6--twitch--ccu--forecast--01-blue)](https://make.fun/competitions/gta6-twitch-ccu-forecast-01)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, high-performance hourly Twitch CCU forecaster for Grand Theft Auto VI launch day (Hours 2 to 24, UTC), built for the `gta6-twitch-ccu-forecast-01` competition.

## Methodology

"Unlock-aligned log-ratio comparables forecaster with kernel-weighted per-hour quantile estimation":
1. **Log-Ratio Dynamics**: For each comparable historical launch, computes hourly log-ratios $r_h = \ln(v_h / v_1)$ relative to hour 1.
2. **Kernel Weighting**: Applies a Gaussian kernel on scale differences $\ln(v_1) - \ln(p_1)$ to weight historical launches most similar in scale and viewer profile to GTA VI's hour 1 print.
3. **Quantile Spread Estimation**: Computes weighted empirical quantiles ($\tau \in \{0.05, 0.25, 0.50, 0.75, 0.95\}$) of log-ratios for each hour $2 \dots 24$.
4. **Calibration & Monotonicity**: Projects forecast quantiles back to viewer space ($\hat{q}_\tau = p_1 \cdot \exp(r_\tau)$), enforces strict monotonicity (non-decreasing quantiles), and applies rounding.

## Performance
- **Log-Scale Pinball Loss**: Achieves ~0.2246 average loss across leave-one-out cross-validation on 37 historical comparable launches (a **51.68% improvement** over the house baseline of 0.4648).
- **Execution Time**: Runs in ~0.3 seconds per case (well within the 8-second limit).
- **Determinism**: 100% deterministic (two runs produce byte-identical outputs).

## Usage
Standard library Python 3.13:
```bash
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=output python3 main.py
```
