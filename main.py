from skimmer import AnalysisSkimmer

def main():
    # --- Configuration ---
   # INPUT_FILE = "/uscms/home/msahoo/nobackup/Project_tzq/EGamma2022_EraF_v15.root" # Change this to your file path
    INPUT_FILE = "root://cmsxrootd.fnal.gov//store/mc/Run3Summer22EENanoAODv12/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/30000/08e731fc-4afd-485c-a775-dc422c30ed94.root"
    OUTPUT_FILE = "output_filtered.root"
    TREE_NAME = "Events"

    # Define Triggers (OR Logic)
    # Events passing ANY of these will be kept
    TRIGGERS = [
        "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "HLT_Ele32_WPTight_Gsf",
        "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"
    ]

    # Define MET Filters (AND Logic)
    # Events must pass ALL of these to be kept
    MET_FILTERS = [
        "Flag_goodVertices",
        "Flag_HBHENoiseFilter",
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter",
        "Flag_BadPFMuonDzFilter",
        "Flag_eeBadScFilter"
    ]

    # --- Execution ---
    
    # 1. Initialize
    skimmer = AnalysisSkimmer(INPUT_FILE, TREE_NAME)
    
    skimmer.define_total_weight(1,1)
    # 3. Apply Global Filters
    skimmer.apply_global_filters(triggers=TRIGGERS, met_filters=MET_FILTERS)
    
    extra_branches=["PuppiMET_pt","nMuon","nElectron"]

    # 4. Run and Save
    skimmer.save_snapshot(OUTPUT_FILE, extra_branches)

if __name__ == "__main__":
    main()
