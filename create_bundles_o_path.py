import os
import json
import subprocess


def query_das(dataset):
    """
    Query DAS and return list of ROOT files.
    """
    print(f"Querying DAS for dataset:\n  {dataset}")

    cmd = f'dasgoclient --query="file dataset={dataset}"'

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"DAS error:\n{stderr.decode()}")

    files = stdout.decode().strip().split("\n")
    return [f for f in files if f]


def create_bundles_from_dataset_txt(
    txt_file,
    files_per_part=25,
    output_json="Big_2024_MC_file.json",
    redirector="root://cmsxrootd.fnal.gov/"
):
    """
    Reads dataset + metadata from txt file.
    Queries DAS.
    Splits files into parts.
    Writes structured JSON including metadata.
    """

    if not os.path.exists(txt_file):
        raise FileNotFoundError(f"{txt_file} not found")

    # Load existing JSON if present
    full_cache = {}
    if os.path.exists(output_json):
        with open(output_json, "r") as f:
            try:
                full_cache = json.load(f)
            except json.JSONDecodeError:
                full_cache = {}

    with open(txt_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:

        parts = line.split()

        if len(parts) < 2:
            print(f"Skipping malformed line: {line}")
            continue

        dataset = parts[0]
        tag = parts[1]

        # ---- Default metadata ----
        cross_section = None
        sum_genweight = None
        is_data = False

        # Parse metadata
        if len(parts) >= 3:
            if parts[2].upper() == "DATA":
                is_data = True
            else:
                cross_section = float(parts[2])

        if len(parts) >= 4:
            sum_genweight = float(parts[3])

        print(f"\nProcessing tag: {tag}")
        print(f"  is_data = {is_data}")
        print(f"  cross_section = {cross_section} in pb")
        print(f"  sum_genweight = {sum_genweight}")

        # ---- Query DAS ----
        lfns = query_das(dataset)
        files = [redirector + lfn for lfn in lfns]
        total_files = len(files)

        if total_files == 0:
            print(f"No files found for {tag}")
            continue

        print(f"Total files for {tag}: {total_files}")

        # ---- Build structured tag dictionary ----
        tag_dict = {
            "metadata": {
                "cross_section_pb": cross_section,
                "sum_genweight": sum_genweight,
                "is_data": is_data
            },
            "files": {}
        }

        # ---- Split into parts ----
        part_counter = 1
        for i in range(0, total_files, files_per_part):
            chunk = files[i: i + files_per_part]
            tag_dict["files"][f"part{part_counter}"] = chunk
            part_counter += 1

        print(f"  -> Created {part_counter - 1} parts for {tag}")

        # Store in global cache
        full_cache[tag] = tag_dict

    # ---- Write JSON ----
    with open(output_json, "w") as f:
        json.dump(full_cache, f, indent=4)

    print(f"\nSuccess: JSON written to {output_json}")


# ------------------ Entry Point ------------------

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python create_bundles_o_path.py datasets.txt")
        sys.exit(1)

    txt_file = sys.argv[1]

    create_bundles_from_dataset_txt(
        txt_file=txt_file,
        files_per_part=25,
        output_json="Big_2024_MC_file.json"
    )

