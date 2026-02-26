import ROOT
import subprocess
import json
from datetime import datetime

# === User Config ===
redirector = "root://cmsxrootd.fnal.gov/"
dataset_file = "GetGnWeight.txt"

output_file = "genweight_results.txt"
json_output_file = "genweight_results.json"


# ---------------------------------------------------------
# Read datasets from txt file
# ---------------------------------------------------------
def read_datasets(filename):
    with open(filename) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return lines


# ---------------------------------------------------------
# DAS query
# ---------------------------------------------------------
def get_das_files(dataset):
    cmd = ["dasgoclient", "-query", f"file dataset={dataset}"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[ERROR] DAS failed for {dataset}")
        return []

    files = result.stdout.strip().split("\n")
    return [redirector + f for f in files if f.strip()]


# ---------------------------------------------------------
# RDataFrame genEventSumw calculation
# ---------------------------------------------------------
def sum_genEventSumw_rdf(files):

    if not files:
        return 0.0

    try:
        df = ROOT.RDataFrame("Runs", files)
        total = df.Sum("genEventSumw").GetValue()
        return total

    except Exception as e:
        print(f"[ERROR] RDF failed: {e}")
        return 0.0


# ---------------------------------------------------------
def get_short_name(dataset):
    parts = dataset.split("/")
    return parts[1] if len(parts) > 1 else dataset


# ---------------------------------------------------------
def process_all():

    datasets = read_datasets(dataset_file)

    results = {}
    summary_lines = []

    print(f"Processing {len(datasets)} datasets")
    print("="*80)

    for i, dataset in enumerate(datasets, 1):

        short_name = get_short_name(dataset)
        print(f"\n[{i}/{len(datasets)}] {short_name}")

        files = get_das_files(dataset)

        if not files:
            print("  No files found.")
            results[short_name] = {
                "dataset": dataset,
                "total_genEventSumw": 0.0,
                "num_files": 0,
                "status": "failed"
            }
            continue

        print(f"  Found {len(files)} files")

        total_sumw = sum_genEventSumw_rdf(files)

        results[short_name] = {
            "dataset": dataset,
            "total_genEventSumw": float(total_sumw),
            "num_files": len(files),
            "status": "success"
        }

        summary = f"{short_name}: {total_sumw:.2f} ({len(files)} files)"
        summary_lines.append(summary)

        print("  →", summary)

    return results, summary_lines


# ---------------------------------------------------------
def save_results(results, summary_lines):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # TEXT
    with open(output_file, "w") as f:
        f.write(f"Generated on: {timestamp}\n")
        f.write("="*80 + "\n\n")

        for line in summary_lines:
            f.write(line + "\n")

    # JSON
    with open(json_output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "results": results
        }, f, indent=2)

    print("\nSaved:")
    print("  ", output_file)
    print("  ", json_output_file)


# ---------------------------------------------------------
if __name__ == "__main__":

    ROOT.ROOT.EnableImplicitMT()   # Multithreading

    results, summary_lines = process_all()
    save_results(results, summary_lines)

    print("\nDone.")

