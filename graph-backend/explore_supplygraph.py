import argparse, json
from pathlib import Path
import pandas as pd

def explore_csv(f):
    df = pd.read_csv(f)
    print(f"\n--- {f.name} ---\nRows: {len(df)} | Columns: {list(df.columns)}")
    print(df.head(3).to_string())

def explore_json(f):
    data = json.load(open(f))
    print(f"\n--- {f.name} ---")
    if isinstance(data, list):
        print(f"list of {len(data)} items")
        if data: print(json.dumps(data[0], indent=2)[:500])
    elif isinstance(data, dict):
        print("keys:", list(data.keys()))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--path", default="data/raw")
    args = p.parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"'{root}' not found - download SupplyGraph into it first.")
        exit()
    files = list(root.rglob("*.csv")) + list(root.rglob("*.json"))
    for f in files:
        (explore_csv if f.suffix == ".csv" else explore_json)(f)
