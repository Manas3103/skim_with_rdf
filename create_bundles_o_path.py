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
        cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"DAS error:\n{stderr.decode()}")

    files = stdout.decode().strip().split("\n")
    return [f for f in files if f]

def create_bundles_from_dataset_txt(txt_file, files_per_part=10, output_json="file_cache.json", redirector="root://cmsxrootd.fnal.gov/"):
    """
    Reads dataset + tag from txt file.
    Queries DAS.
    Splits files into parts of size 'files_per_part'.
    Writes structured JSON.
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
        # Expecting line format: /Dataset/Path TAG
        parts = line.split()
        if len(parts) < 2:
            print(f"Skipping malformed line: {line}")
            continue
            
        dataset, tag = parts[0], parts[1]

        # Query DAS
        lfns = query_das(dataset)
        files = [redirector + lfn for lfn in lfns]
        total_files = len(files)

        if total_files == 0:
            print(f"No files found for {tag}")
            continue

        print(f"Total files for {tag}: {total_files}")

        tag_dict = {}
        # Chunk the files list into groups of files_per_part
        # i represents the starting index of each chunk
        part_counter = 1
        for i in range(0, total_files, files_per_part):
            chunk = files[i : i + files_per_part]
            tag_dict[f"part{part_counter}"] = chunk
            part_counter += 1

        print(f"  -> Created {part_counter - 1} parts for {tag}")

        # Add to global JSON
        full_cache[tag] = tag_dict

    # Write JSON
    with open(output_json, "w") as f:
        json.dump(full_cache, f, indent=4)

    print(f"\nSuccess: JSON written to {output_json}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python create_bundles_o_path.py datasets.txt")
        sys.exit(1)

    txt_file = sys.argv[1]

    # Set files_per_part=10 as requested
    create_bundles_from_dataset_txt(
        txt_file=txt_file,
        files_per_part=10,
        output_json="file_cache.json"
    )
