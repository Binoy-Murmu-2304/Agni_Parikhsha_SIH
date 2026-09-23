import os
import json
import argparse
from pathlib import Path

from agnipariksha.data_generator.generator import AgniSimGenerator

def main():
    parser = argparse.ArgumentParser(description="AGNI-SIM Dataset Generator")
    parser.add_argument("--out_dir", type=str, default="data", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    gen = AgniSimGenerator()
    
    print("Generating main dataset...")
    df_main, manifest = gen.generate_dataset(num_lots=50, components_per_lot=2000)
    
    main_csv = out_dir / "dataset.csv"
    df_main.to_csv(main_csv, index=False)
    print(f"Saved {len(df_main)} rows to {main_csv}")
    
    manifest_file = out_dir / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest to {manifest_file}")
    
    print("Generating stress set...")
    df_stress = gen.generate_stress_set(components_per_mech=100)
    stress_csv = out_dir / "stress_set.csv"
    df_stress.to_csv(stress_csv, index=False)
    print(f"Saved {len(df_stress)} rows to {stress_csv}")

if __name__ == "__main__":
    main()
