import ROOT
import os
import subprocess
import sys
import time
from skimmer import AnalysisSkimmer
import config 

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

    def get_file_list(self):
        """
        Smart caching logic: Checks for a dataset-specific text file.
        If missing, queries DAS and creates it.
        """
        # Create a safe filename like 'filelist_MuonEG_Run2022D.txt'
        safe_name = self.cfg.DATASET_NAME.replace("/", "_")[1:]
        cache_filename = f"filelist_{safe_name}.txt"

        if os.path.exists(cache_filename):
            print(f"Loading cached file list: {cache_filename}")
            with open(cache_filename, "r") as f:
                self.files = [line.strip() for line in f]
        else:
            print(f"Cache not found. Fetching from DAS...")
            lfns = self._query_das()
            self.files = [self.cfg.REDIRECTOR + lfn for lfn in lfns]
            
            # Save the cache
            with open(cache_filename, "w") as f:
                for item in self.files:
                    f.write(f"{item}\n")
        
        # Handle the MAX_FILES limit
        total_available = len(self.files)
        if self.cfg.MAX_FILES and self.cfg.MAX_FILES < total_available:
            print(f"Limiting processing to {self.cfg.MAX_FILES} / {total_available} files.")
            self.files = self.files[:self.cfg.MAX_FILES]
        else:
            print(f"Processing all {total_available} files.")

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
        self.print_stats()

# --- Entry Point ---
if __name__ == "__main__":
    # Create the runner with the imported config module
    runner = AnalysisRunner(config)
    runner.run()
