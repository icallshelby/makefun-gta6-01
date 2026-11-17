import json
from pathlib import Path
import math
import statistics

def round2(x: float) -> float | int:
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value

def pinball_loss_log(y_true, q_pred, tau):
    if y_true < 1:
        y_true = 1
    if q_pred < 1:
        q_pred = 1
    y_log = math.log(y_true)
    q_log = math.log(q_pred)
    diff = y_log - q_log
    if diff >= 0:
        return tau * diff
    else:
        return (1 - tau) * (-diff)

def evaluate_comparables():
    p = Path('input/p00.in')
    data = json.loads(p.read_text())
    comps = data.get('comparables', [])
    
    levels = [0.05, 0.25, 0.50, 0.75, 0.95]
    Z = [-1.645, -0.674, 0, 0.674, 1.645]
    SIGMA = 0.15
    
    # House baseline losses
    baseline_losses = []
    # Our comparables model losses
    our_losses = []
    
    valid_comps = []
    for c in comps:
        ds = c['day_start']
        hourly = {h['from']: h['viewers'] for h in c['hourly']}
        from datetime import datetime, timedelta
        dt = datetime.fromisoformat(ds.replace('Z', '+00:00'))
        seq = []
        ok = True
        for h_idx in range(1, 25):
            t_str = (dt + timedelta(hours=h_idx-1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            if t_str not in hourly:
                ok = False
                break
            seq.append(max(1, hourly[t_str]))
        if ok:
            valid_comps.append((c['name'], seq))
            
    print(f"Evaluating on {len(valid_comps)} valid comparable games using leave-one-out CV...")
    
    # House baseline evaluation
    base_total_loss = 0.0
    base_count = 0
    for i, (name, seq) in enumerate(valid_comps):
        p1 = seq[0]
        for h_idx in range(2, 25):
            h = h_idx
            y_true = seq[h_idx-1]
            # baseline quantiles
            qs = [p1 * math.exp(z * SIGMA * math.sqrt(h - 1)) for z in Z]
            for tau, q in zip(levels, qs):
                base_total_loss += pinball_loss_log(y_true, q, tau)
                base_count += 1
                
    base_avg_loss = base_total_loss / base_count
    print(f"House baseline avg log pinball loss: {base_avg_loss:.4f}")
    
    # Comparables model evaluation (leave-one-out)
    our_total_loss = 0.0
    our_count = 0
    
    for i, (test_name, test_seq) in enumerate(valid_comps):
        train_comps = [seq for j, (name, seq) in enumerate(valid_comps) if j != i]
        test_p1 = test_seq[0]
        
        # For each hour 2..24
        for h_idx in range(2, 25):
            h = h_idx
            y_true = test_seq[h_idx-1]
            
            # Collect log ratios r_h = ln(v_h / v_1) from training comparables
            r_list = []
            weights = []
            for train_seq in train_comps:
                tr_p1 = train_seq[0]
                tr_vh = train_seq[h_idx-1]
                r = math.log(tr_vh / tr_p1)
                # Kernel weight based on scale difference ln(tr_p1) vs ln(test_p1)
                dist = abs(math.log(tr_p1) - math.log(test_p1))
                w = math.exp(-0.5 * (dist / 2.0) ** 2) # bandwidth 2.0 in log space
                r_list.append(r)
                weights.append(w)
                
            # Weighted quantile calculation
            # Sort by r
            combined = sorted(zip(r_list, weights), key=lambda x: x[0])
            total_w = sum(w for r, w in combined)
            if total_w == 0:
                total_w = len(combined)
                combined = [(r, 1.0) for r, w in combined]
                
            def weighted_quantile(sorted_cw, tau):
                cumulative = 0.0
                target = tau * total_w
                for r, w in sorted_cw:
                    cumulative += w
                    if cumulative >= target:
                        return r
                return sorted_cw[-1][0]
                
            qs = []
            for tau in levels:
                r_tau = weighted_quantile(combined, tau)
                q_val = test_p1 * math.exp(r_tau)
                # fallback or baseline smoothing if q_val is unreasonable
                qs.append(q_val)
                
            # Ensure non-decreasing and bounds
            # Sort qs
            qs.sort()
            for tau, q in zip(levels, qs):
                our_total_loss += pinball_loss_log(y_true, max(1.0, q), tau)
                our_count += 1
                
    our_avg_loss = our_total_loss / our_count
    print(f"Our comparables model avg log pinball loss: {our_avg_loss:.4f}")
    improvement = (base_avg_loss - our_avg_loss) / base_avg_loss * 100
    print(f"Improvement over baseline: {improvement:.2f}%")

if __name__ == '__main__':
    evaluate_comparables()
