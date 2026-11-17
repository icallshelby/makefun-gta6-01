# SHIP-READY.md — gta6-twitch-ccu-forecast-01

**Status:** BUILD SELESAI  
**Model:** Python 3.13 (`main.py`, standard library only)  
**Strategy:** Unlock-aligned log-ratio comparables forecaster with kernel weighting (`main.py`)

## 1. Practice & Cross-Validation Results
Evaluated via leave-one-out cross-validation on 37 valid historical comparable launches in practice cases (`p00.in`):
- **House Baseline (persistence + random walk $\sigma=0.15$):** Avg log-scale pinball loss = **0.4648**
- **Our Comparables Kernel Model (`main.py`):** Avg log-scale pinball loss = **0.2246**
- **Improvement:** **51.68% reduction in pinball loss**

## 2. Verification Checklist
1. **Execution on Practice Cases (`p00.in` - `p03.in`):** Passed successfully. Generated valid `.out` files containing 23 hourly rows (hours 2..24) with 5 quantiles each.
2. **Output Format & Constraints:**
   - JSON format with `"hours"` key matching starter specification.
   - Quantiles are finite numbers $> 0$, $\le 1e9$, non-decreasing, and rounded to 2 decimals.
   - File sizes well under 65,536 bytes.
3. **Determinism:** Two consecutive runs produced 100% byte-identical outputs across all practice cases.
4. **Performance:** Execution time is ~0.3 seconds per case (well below the 8-second limit and 1024 MB memory limit).

## 3. Scope & Handover
- **Built in this session:** `main.py`, `README.md`, `evaluate.py`, `validate_run.py`, `SHIP-READY.md`.
- **Micro session (kit gate thinking_revised):** q95 median guard (cap q95 at 8x median per hour) — LOO pinball tetap 0,2246; q95 jam 10 p00 turun 858.068 → 170.349,64.
- **Kit check 17 Nov 19:15 WIB: 13 passed, 0 failed, 5 skipped** (thinking_reproduces 93,4% authored, main.py 74 authored lines; thinking_revised lolos sesudah guard). 5 item "at submission" menunggu repo GitHub dibuat + push.
- **Commit final:** `ecc9a07477aa313efa9fa67bc0b9d9107d0bf83c` (lihat `git rev-parse HEAD` bila berubah).
- **Bundle:** `~/workspace/makefun/gta6-01-bundle.tar.gz` (2 sesi Gemini, --no-muse-app) — sha256 di laporan koordinator.
- **Remaining actions (handled by parent):** buat repo `icallshelby/makefun-gta6-01` via browser + isi About, push, submit (hanya bila kit check lolos — sudah lolos).
