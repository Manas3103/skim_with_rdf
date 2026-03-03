This package it to skim the .root file and save it in the /EOS area.

# DAS Dataset Bundler JSON Generator

## Overview

This script automatically:

Queries CMS DAS for ROOT files
Reads datasets from a text configuration file
Splits files into manageable job parts
Stores metadata (cross-section, genweight, data flag)
Produces a structured JSON file for batch/Condor processing

The output JSON can be directly used for skimming, NanoAOD processing, or distributed analysis workflows.

---

## Script

```
create_bundles_o_path.py
```

---

## Requirements

Make sure the following are available:

* Python 3.8
* CMS environment initialized
* DAS client available

Load CMS environment:

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsenv
```

Check DAS:

```bash
dasgoclient --help
```

---

## Input File Format (`datasets.txt`)

Each line describes **one dataset**.

### General Format

```
DATASET_PATH   TAG   CROSS_SECTION(pb)/DATA   SUM_GENWEIGHT(optional)
```

---

### Case 1 — Monte Carlo Sample

```
/DYJetsToLL_M-50_TuneCP5_13TeV/.../NANOAODSIM  DYJets  6077.22  1.23e10
```

Meaning:

| Field         | Description                    |
| ------------- | ------------------------------ |
| DATASET_PATH  | Official DAS dataset           |
| TAG           | Short process name             |
| CROSS_SECTION | Production cross section in pb |
| SUM_GENWEIGHT | Total generator weight         |

---

### Case 2 — Data Sample

For data, replace cross-section with:

```
DATA
```

Example:

```
/MuonEG/Run2022D-NanoAOD/.../NANOAOD  MuonEG_Run2022D  DATA
```

Meaning:

* Automatically sets:

  * `is_data = true`
  * No cross-section required
  * No genweight required

---

### Valid Examples

```
/tZq_ll_4f_TuneCP5_13TeV/.../NANOAODSIM   tZq     0.0758   4.52e7
/TTZToLLNuNu_M-10/.../NANOAODSIM          ttZ     0.2529   9.87e8
/MuonEG/Run2022D-NanoAOD/.../NANOAOD      DataEG  DATA
```

---

## Running the Script

### Basic Usage

```bash
python3 create_bundles_o_path.py datasets.txt
```

---

## What the Script Does

For every dataset:

1. Queries DAS:

   ```
   dasgoclient --query="file dataset=DATASET"
   ```

2. Retrieves all ROOT files

3. Adds redirector:

   ```
   root://cmsxrootd.fnal.gov/
   ```

4. Splits files into parts
   (default = **25 files per part**)

5. Writes structured JSON output

---

## Output File

Default output:

```
Big_2024_MC_file.json
```

---

## Output JSON Structure

Example:

```json
{
  "tZq": {
    "metadata": {
      "cross_section_pb": 0.0758,
      "sum_genweight": 45200000.0,
      "is_data": false
    },
    "files": {
      "part1": [
        "root://cmsxrootd.fnal.gov//store/..."
      ],
      "part2": [
        "root://cmsxrootd.fnal.gov//store/..."
      ]
    }
  }
}
```

---

## Meaning of JSON Fields

### metadata

| Key              | Meaning              |
| ---------------- | -------------------- |
| cross_section_pb | MC cross section     |
| sum_genweight    | normalization weight |
| is_data          | true for real data   |

---

### files

Each part corresponds to one Condor/job submission unit.

Example:

```
process = tZq
part    = part3
```

---

## Customization

### Change files per job

Inside script:

```python
files_per_part=25
```

Example:

```python
files_per_part=10
```

---

### Change output JSON name

```python
output_json="MySamples.json"
```

---

## Typical Workflow

```
datasets.txt
      ↓
create_bundles_o_path.py
      ↓
Big_2024_MC_file.json
      ↓
Condor / Skimmer jobs
```

---

## Common Errors

### DAS command not found

Load CMS environment:

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
```

---

### Dataset returns zero files

Check dataset exists:

```bash
dasgoclient --query="dataset dataset=*NAME*"
```

---


