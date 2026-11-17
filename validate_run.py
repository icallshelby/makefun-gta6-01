import subprocess
import os
import json
from pathlib import Path
import time
import hashlib
import sys

def run_validation():
    input_dir = Path("input")
    output_dir = Path("out_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    env = os.environ.copy()
    env["MAKEFUN_INPUT_DIR"] = str(input_dir)
    env["MAKEFUN_OUTPUT_DIR"] = str(output_dir)
    
    print("Running main.py (Run 1)...")
    start_time = time.time()
    res1 = subprocess.run(["python3", "main.py"], env=env, capture_output=True, text=True)
    duration1 = time.time() - start_time
    print(f"Run 1 completed in {duration1:.3f}s. Exit code: {res1.returncode}")
    if res1.returncode != 0:
        print("STDOUT:", res1.stdout)
        print("STDERR:", res1.stderr)
        return False
        
    # Capture hashes of outputs
    hashes_run1 = {}
    for out_path in sorted(output_dir.glob("*.out")):
        hashes_run1[out_path.name] = hashlib.sha256(out_path.read_bytes()).hexdigest()
        
    print("Running main.py (Run 2 - Determinism check)...")
    start_time = time.time()
    res2 = subprocess.run(["python3", "main.py"], env=env, capture_output=True, text=True)
    duration2 = time.time() - start_time
    print(f"Run 2 completed in {duration2:.3f}s. Exit code: {res2.returncode}")
    
    for out_path in sorted(output_dir.glob("*.out")):
        h2 = hashlib.sha256(out_path.read_bytes()).hexdigest()
        if hashes_run1[out_path.name] != h2:
            print(f"ERROR: Determinism failed for {out_path.name}!")
            return False
            
    print("Determinism check passed: two runs produced byte-identical outputs.")
    
    # Validate structure of outputs
    for out_path in sorted(output_dir.glob("*.out")):
        content = out_path.read_text(encoding="utf-8")
        size = len(content.encode("utf-8"))
        if size > 65536:
            print(f"ERROR: {out_path.name} size {size} bytes exceeds 65536 limit!")
            return False
        data = json.loads(content)
        hours = data.get("hours", [])
        if len(hours) != 23:
            print(f"ERROR: {out_path.name} has {len(hours)} rows instead of 23!")
            return False
        expected_hour = 2
        for row in hours:
            if row["hour"] != expected_hour:
                print(f"ERROR: Expected hour {expected_hour}, got {row['hour']}")
                return False
            q = row["q"]
            if len(q) != 5:
                print(f"ERROR: Hour {expected_hour} has {len(q)} quantiles instead of 5")
                return False
            # Check non-decreasing and positive
            prev = 0
            for val in q:
                if not isinstance(val, (int, float)) or val <= 0 or val > 1e9:
                    print(f"ERROR: Invalid quantile value {val} at hour {expected_hour}")
                    return False
                if val < prev:
                    print(f"ERROR: Quantiles not non-decreasing at hour {expected_hour}: {q}")
                    return False
                prev = val
            expected_hour += 1
            
    print("All output structure and validation checks passed successfully!")
    return True

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
