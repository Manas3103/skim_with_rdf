import ROOT
from typing import List, Union

# Enable multi-threading for speed
ROOT.ROOT.EnableImplicitMT()

class AnalysisSkimmer:
    def __init__(self, input_files: Union[str, List[str]], tree_name: str):
        self.df = ROOT.RDataFrame(tree_name, input_files)
        self.input_files = input_files
        self.output_branches = []
        print(f"Initialized RDataFrame with tree '{tree_name}'")


    def apply_global_filters(self, triggers: List[str] = [], met_filters: List[str] = []):
        """
        Applies Triggers (OR logic) and MET Filters (AND logic) if provided.
        """

        # 1. Apply Triggers (OR)
        if triggers:
            self.df = self.df.Filter(" || ".join(triggers), "Combined Trigger Cut")
            print(f"Applied {len(triggers)} Triggers")
        

        # 2. Apply MET Filters (AND)
        if met_filters:
            self.df = self.df.Filter(" && ".join(met_filters), "Combined MET Cut")
            print(f"Applied {len(met_filters)} MET Filters")
        
        self.df = self.df.Filter("PV_npvsGood > 0 && nJet>0 && nMuon + nElectron >= 3", "Has Good PV atleat one jet only 3 L")
        print("3 Lepton >1 jet and the GOOD_PV cut is applied")

        return self.df


    def define_total_weight(self, cross_section, sum_gen_weight):
        print(f"Defining Total Normalization Weight")
        print(f"  > Cross Section: {cross_section}")
        print(f"  > SumOfGenWeight:    {sum_gen_weight}")

        # 2. Calculate the global scaling factor
        #    Formula: Scale = (CrossSection) / SumGenWeight
        if sum_gen_weight != 0:
            global_scale = (cross_section) / sum_gen_weight
        else:
            print("WARNING: SumGenWeight is 0. Setting scale to 0.")
            global_scale = 0

        # 3. Define the new weight branch
        #    Formula: totalWeight = genWeight * global_scale
        # after computing global_scale (before Define)
        self.df = self.df.Define("globalScale", f"{global_scale}") \
                         .Define("sumGenWeight", f"{sum_gen_weight}") \
                         .Define("crossSection", f"{cross_section}") \
                         .Define("totalWeight", f"genWeight * {global_scale}")

        # 4. Add to save list
        self.output_branches.extend(["totalWeight", "globalScale", "sumGenWeight", "crossSection"])
        return self

    def build_branch_list(self, explicit_branches, wildcard_patterns=None):
        """
        Combine explicit branches + wildcard branches
        into one final list using the RDataFrame schema.
        """

        final_branches = list(explicit_branches)

        if not wildcard_patterns:
            return final_branches

        print("Expanding wildcard branches in Skimmer...")

        all_branches = [str(b) for b in self.df.GetColumnNames()]
        
        for pattern in wildcard_patterns:
            prefix = pattern.replace("*", "")
            matches = [b for b in all_branches if b.startswith(prefix)]

            print(f"[INFO] Found {len(matches)} branches for {pattern}")
            final_branches.extend(matches)

        # clean list
        #final_branches = (final_branches)
        print(f"Total branches to save: {len(final_branches)}")

        return final_branches


    def save_snapshot(self, output_filename: str, extra_branches: List[str] = None):
        if extra_branches:
            self.output_branches.extend(extra_branches)
            
        print(f"Saving {len(self.output_branches)} branches to {output_filename}...")
        
        node = ROOT.RDF.AsRNode(self.df)

        branch_vector = ROOT.std.vector('string')()
        for branch in self.output_branches:
            branch_vector.push_back(branch)
        try:
            ROOT.RDF.Experimental.AddProgressBar(node)
        except:
            print("The progress bar is not supporting !! ")
            pass # Older ROOT versions might not have this

        report = self.df.Report()

        # Run Snapshot (Event Loop happens here)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "RECREATE"
        self.df.Snapshot("Events", output_filename, branch_vector, opts)

        # Call the helper function to add the histogram

        print("\n--- Cut Flow Report ---")
        report.Print()


