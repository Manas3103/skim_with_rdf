import ROOT
import os
import subprocess
import sys
import time
from skimmer import AnalysisSkimmer
import config 
import json

class AnalysisRunner:
    def __init__(self, config_module, process_tag=None, part_tag=None):
        """
        Initialize with the configuration module.
        """
        self.cfg = config_module
        self.process_tag = process_tag
        self.part_tag = part_tag
        self.files = []
        self.start_time = 0
        self.end_time = 0
        
        # Enable multi-threading immediately
        ROOT.ROOT.EnableImplicitMT()

    def _query_das(self):
        """Private method to run the DAS command."""
        print(f"Querying DAS for: {self.cfg.DATASET_NAME} ...")
        cmd = f'dasgoclient --query="file dataset={self.cfg.DATASET_NAME}"'
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"DAS Error: {stderr.decode()}")
            
            files = stdout.decode().strip().split('\n')
            return [f for f in files if f]
        except Exception as e:
            print(f"FATAL: {e}")
            sys.exit(1)

    def get_file_list(self):

        cache_filename = self.cfg.JSON_FILE
        print(f"The cache file {cache_filename} is being used")

        if not os.path.exists(cache_filename):
            raise RuntimeError(f"{cache_filename} not found!")

        with open(cache_filename, "r") as f:
            cache_data = json.load(f)

        if self.process_tag not in cache_data:
            raise RuntimeError(f"Process '{self.process_tag}' not found")

        # ---- Extract process block ----
        process_block = cache_data[self.process_tag]

        # ---- Extract metadata ----
        metadata = process_block.get("metadata", {})
        files_dict = process_block.get("files", {})

        # Store metadata in runner
        self.cross_section = metadata.get("cross_section_pb")
        self.sum_genweight = metadata.get("sum_genweight")
        self.is_data = metadata.get("is_data", False)

        print("Metadata loaded:")
        print(f"  is_data        = {self.is_data}")
        print(f"  cross_section  = {self.cross_section}")
        print(f"  sum_genweight  = {self.sum_genweight}")

        if not files_dict:
            raise RuntimeError("No file parts found for this process")

        # ---- If ALL return all parts ----
        if self.part_tag.upper() == "ALL":
            print(f"Running ALL parts for {self.process_tag}")
            return files_dict

        # ---- If single part ----
        if self.part_tag not in files_dict:
            raise RuntimeError(f"Part '{self.part_tag}' not found")

        return {self.part_tag: files_dict[self.part_tag]}


    def start_timer(self):
        self.start_time = time.time()
        print(f"--- Process Started: {time.ctime(self.start_time)} ---")

    def print_stats(self):
        """Calculates and prints the elapsed time."""
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        print("-" * 40)
        print("Analysis Summary")
        print("-" * 40)
        print(f"Files Processed : {len(self.files)}")
        print(f"Output File     : {self.cfg.OUTPUT_FILE}")
        print(f"Total Time      : {hours}h {minutes}m {seconds}s")
        print("-" * 40)

    def run(self):

        self.start_timer()

        # Get parts dictionary
        parts_dict = self.get_file_list()

        if not parts_dict:
            print("No files to process. Exiting.")
            return

        # Loop over parts sequentially
        for part_name, file_list in parts_dict.items():

            print("\n" + "="*50)
            print(f"Processing {self.process_tag} - {part_name}")
            print(f"Files in this part: {len(file_list)}")
            print("="*50)

            # Initialize skimmer
            skimmer = AnalysisSkimmer(file_list, self.cfg.TREE_NAME)

            is_data = any("/store/data/" in f for f in file_list)
            
            print("Calculating total weight...")

            if not self.is_data:

                if self.cross_section is None or self.sum_genweight is None:
                    raise RuntimeError(
                        "MC sample missing cross_section or sum_genweight in metadata"
                    )

                print("Calculating normalization factor from metadata")
                print(f"  cross_section  = {self.cross_section}")
                print(f"  sum_genweight  = {self.sum_genweight}")

                skimmer.define_total_weight(self.cross_section, self.sum_genweight)

            else:
                print("This is a data sample skipping normalization")

            print("Applying filters...")
            skimmer.apply_global_filters(
                triggers=self.cfg.TRIGGERS,
                met_filters=self.cfg.MET_FILTERS
            )
            
            if not is_data:
                branches_input = self.cfg.BRANCHES_TO_SAVE + ([] if is_data else self.cfg.BRANCHES_MC)
                branches_to_save = skimmer.build_branch_list(
                    branches_input,
                    getattr(self.cfg, "BRANCHES_WILDCARD", None)
                )
                print("Branch required for MC process")
            else:
                branches_to_save = skimmer.build_branch_list(
                    self.cfg.BRANCHES_TO_SAVE,
                    getattr(self.cfg, "BRANCHES_WILDCARD_DATA", None)
                )
                print("Branch required for MC process")


            # Create part-specific output name
            output_name = f"{self.process_tag}_{part_name}.root"

            print(f"Writing output to {output_name}")

            try:
                skimmer.save_snapshot(output_name, branches_to_save)
                print(f"{output_name} saved successfully.")
            except Exception as e:
                print(f"ERROR during {part_name}: {e}")
                continue

        self.print_stats()


# --- Entry Point ---
#if __name__ == "__main__":
    # Create the runner with the imported config module
#    runner = AnalysisRunner(config)
#    runner.run()

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python runner.py PROCESS_TAG PART_TAG")
        print("Example:")
        print("  python runner.py WZ_3L ALL")
        sys.exit(1)

    process_tag = sys.argv[1]
    part_tag = sys.argv[2]

    runner = AnalysisRunner(
        config,
        process_tag=process_tag,
        part_tag=part_tag
    )

    runner.run()

