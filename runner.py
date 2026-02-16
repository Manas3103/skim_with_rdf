import ROOT
import os
import subprocess
import sys
import time
from skimmer import AnalysisSkimmer
import config 
import json

class AnalysisRunner:
    def __init__(self, config_module):
        """
        Initialize with the configuration module.
        """
        self.cfg = config_module
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

'''    def get_file_list(self):
        """
        Uses a single JSON cache file.
        Structure:
        {
            "tag_name": [file1, file2, ...],
            ...
        }
        """

        cache_filename = "file_cache.json"

        # Use dataset name as tag (safe format)
        tag_name = self.cfg.DATASET_NAME.replace("/", "_")[1:]

        # --------------------------------------------------
        # Step 1: Load existing JSON (if any)
        # --------------------------------------------------
        if os.path.exists(cache_filename):
            with open(cache_filename, "r") as f:
                try:
                    cache_data = json.load(f)
                except json.JSONDecodeError:
                    cache_data = {}
        else:
            cache_data = {}

        # --------------------------------------------------
        # Step 2: If tag exists → load from cache
        # --------------------------------------------------
        if tag_name in cache_data:
            print(f"Loading file list from JSON cache for tag: {tag_name}")
            self.files = cache_data[tag_name]

        else:
            print(f"Tag '{tag_name}' not found in cache. Fetching from DAS...")
            lfns = self._query_das()
            self.files = [self.cfg.REDIRECTOR + lfn for lfn in lfns]

            # Add new tag to JSON
            cache_data[tag_name] = self.files

            # Save updated JSON
            with open(cache_filename, "w") as f:
                json.dump(cache_data, f, indent=4)

        # --------------------------------------------------
        # Step 3: Optional Check for new files in DAS
        # (Only if you want to update automatically)
        # --------------------------------------------------
        # lfns = self._query_das()
        # new_files = [self.cfg.REDIRECTOR + lfn for lfn in lfns]
        #
        # existing_set = set(cache_data.get(tag_name, []))
        # updated = False
        #
        # for file in new_files:
        #     if file not in existing_set:
        #         cache_data[tag_name].append(file)
        #         updated = True
        #
        # if updated:
        #     print("New files detected. Updating JSON cache.")
        #     with open(cache_filename, "w") as f:
        #         json.dump(cache_data, f, indent=4)

        # --------------------------------------------------
        # Step 4: Apply MAX_FILES limit
        # --------------------------------------------------
        total_available = len(self.files)

        if self.cfg.MAX_FILES and self.cfg.MAX_FILES < total_available:
            print(f"Limiting processing to {self.cfg.MAX_FILES} / {total_available} files.")
            self.files = self.files[:self.cfg.MAX_FILES]
        else:
            print(f"Processing all {total_available} files.")'''

    def get_file_list(self):

        cache_filename = "file_cache.json"

        if not os.path.exists(cache_filename):
            raise RuntimeError("file_cache.json not found!")

        with open(cache_filename, "r") as f:
            cache_data = json.load(f)

        if self.process_tag not in cache_data:
            raise RuntimeError(f"Process '{self.process_tag}' not found")

        process_dict = cache_data[self.process_tag]

        # If ALL → return all parts
        if self.part_tag.upper() == "ALL":
            print(f"Running ALL parts for {self.process_tag}")
            return process_dict

        # If single part
        if self.part_tag not in process_dict:
            raise RuntimeError(f"Part '{self.part_tag}' not found")

        return {self.part_tag: process_dict[self.part_tag]}


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

'''    def run(self):
        """
        Main execution method.
        """
        self.start_timer()
        
        # 1. Get Files
        self.get_file_list()
        if not self.files:
            print("No files to process. Exiting.")
            return

        # 2. Initialize Skimmer (from skimmer.py)
        print(f"Initializing RDataFrame...")
        skimmer = AnalysisSkimmer(self.files, self.cfg.TREE_NAME)

        print("calculating sum of genWeight")
        xsec_pb=0.079
        lumi_fb_inv = 62.4
        lumi_pb_inv = lumi_fb_inv * 1000

        #skimmer.define_genweight_sum_branch()
        skimmer.define_total_weight(cross_section=xsec_pb, luminosity=lumi_pb_inv)


        # 3. Apply Cuts (Using values from config)
        print("Applying filters...")
        skimmer.apply_global_filters(triggers=self.cfg.TRIGGERS, met_filters=self.cfg.MET_FILTERS)

        print("Saving Branches")
        branches_to_save = skimmer.build_branch_list(self.cfg.BRANCHES_TO_SAVE,getattr(self.cfg, "BRANCHES_WILDCARD", None))

        for r in branches_to_save:
            print(f"This is saving {r}")

        # 4. Save Output
        print(f"Starting Event Loop (writing to {self.cfg.OUTPUT_FILE})...")
        try:
            skimmer.save_snapshot(self.cfg.OUTPUT_FILE, branches_to_save)
            print("Snapshot saved successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR during execution: {e}")
            sys.exit(1)

        # 5. Finish
        self.print_stats()'''

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

            print("Calculating total weight...")
            xsec_pb = 0.079
            lumi_fb_inv = 62.4
            lumi_pb_inv = lumi_fb_inv * 1000

            skimmer.define_total_weight(
                cross_section=xsec_pb,
                luminosity=lumi_pb_inv
            )

            print("Applying filters...")
            skimmer.apply_global_filters(
                triggers=self.cfg.TRIGGERS,
                met_filters=self.cfg.MET_FILTERS
            )

            branches_to_save = skimmer.build_branch_list(
                self.cfg.BRANCHES_TO_SAVE,
                getattr(self.cfg, "BRANCHES_WILDCARD", None)
            )

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

