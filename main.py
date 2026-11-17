"""GTA VI launch-day Twitch viewers forecaster (comparables log-ratio kernel model).
Python 3.13, standard library only.
"""

import json
import math
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Keep /bot off sys.path if needed, put local directory first
sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.50, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]
SIGMA_BASELINE = 0.15

def round2(x: float) -> float | int:
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value

def weighted_quantile(sorted_cw: list[tuple[float, float]], total_w: float, tau: float) -> float:
    if total_w <= 0 or not sorted_cw:
        return 0.0
    cumulative = 0.0
    target = tau * total_w
    for r, w in sorted_cw:
        cumulative += w
        if cumulative >= target:
            return r
    return sorted_cw[-1][0]

def forecast_case(case: dict, name: str) -> dict:
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1, first["viewers"])
    
    comps = case.get("comparables", [])
    valid_train = []
    for c in comps:
        ds = c.get("day_start")
        if not ds:
            continue
        hourly = {h["from"]: max(1, h["viewers"]) for h in c.get("hourly", [])}
        try:
            dt = datetime.fromisoformat(ds.replace("Z", "+00:00"))
        except Exception:
            continue
        seq = []
        ok = True
        for h_idx in range(1, 25):
            t_str = (dt + timedelta(hours=h_idx-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            if t_str not in hourly:
                ok = False
                break
            seq.append(hourly[t_str])
        if ok and seq[0] > 0:
            valid_train.append(seq)
            
    hours_output = []
    forecast_rows = case.get("forecast", [])
    
    for row in forecast_rows:
        h = row["hour"]
        h_idx = h  # hour 2 corresponds to index 1 (0-based)
        if h_idx < 2 or h_idx > 24:
            # Fallback baseline
            qs = [p1 * math.exp(z * SIGMA_BASELINE * math.sqrt(h - 1)) for z in Z]
        elif not valid_train:
            # Fallback baseline if no valid training comps
            qs = [p1 * math.exp(z * SIGMA_BASELINE * math.sqrt(h - 1)) for z in Z]
        else:
            r_list = []
            weights = []
            for tr_seq in valid_train:
                tr_p1 = tr_seq[0]
                tr_vh = tr_seq[h_idx - 1]
                r = math.log(tr_vh / tr_p1)
                dist = abs(math.log(tr_p1) - math.log(p1))
                w = math.exp(-0.5 * (dist / 2.0) ** 2)
                r_list.append(r)
                weights.append(w)
                
            combined = sorted(zip(r_list, weights), key=lambda x: x[0])
            total_w = sum(w for r, w in combined)
            
            qs = []
            for tau in LEVELS:
                r_tau = weighted_quantile(combined, total_w, tau)
                q_val = p1 * math.exp(r_tau)
                qs.append(q_val)
                
        # Ensure non-decreasing, positive, <= 1e9 (with q95 capped at 8x median)
        qs.sort()
        if len(qs) == 5:
            median_val = qs[2]
            if median_val > 0:
                qs[4] = min(qs[4], median_val * 8.0)
            qs[4] = max(qs[4], qs[3])
            qs.sort()
        # Enforce strict non-decreasing and bounds
        cleaned_qs = []
        prev = 1.0
        for q in qs:
            q_clamped = max(prev, min(1e9, q))
            cleaned_qs.append(round2(q_clamped))
            prev = q_clamped
            
        hours_output.append({"hour": h, "q": cleaned_qs})
        
    return {"hours": hours_output}

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )

if __name__ == "__main__":
    main()
