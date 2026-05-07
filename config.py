# config.py

# --- Dataset & I/O ---
DATASET_NAME = "/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
REDIRECTOR = "root://cmsxrootd.fnal.gov/"
OUTPUT_FILE = "WZ_3L.root"
TREE_NAME = "Events"
JSON_FILE = "JSON_files/Big_2024_MC_file.json"


# Set to an integer (e.g., 5) or None to run on all files
#MAX_FILES = None 
MAX_FILES = 1 


# --- Analysis Cuts ---
# Triggers (OR Logic)
TRIGGERS = [
        "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
	    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
	    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
	    "HLT_Mu37_Ele27_CaloIdL_MW",
	    "HLT_Mu27_Ele37_CaloIdL_MW",
	    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ",
	    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL",
	    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ",
	    "HLT_Ele28_eta2p1_WPTight_Gsf_HT150",
	    "HLT_Ele30_WPTight_Gsf",
	    "HLT_Ele32_WPTight_Gsf",
	    "HLT_Ele35_WPTight_Gsf",
	    "HLT_Ele38_WPTight_Gsf",
	    "HLT_Ele40_WPTight_Gsf",
	    "HLT_Ele115_CaloIdVT_GsfTrkIdT",
	    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
	    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
	    "HLT_DoubleEle33_CaloIdL_MW",
	    "HLT_DoubleEle25_CaloIdL_MW",
	    "HLT_DoubleEle27_CaloIdL_MW",
	    "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL",
	    "HLT_IsoMu24",
	    "HLT_IsoMu24_eta2p1",
	    "HLT_IsoMu27",
	    "HLT_IsoMu50_AK8PFJet230_SoftDropMass40",
	    "HLT_TripleMu_10_5_5_DZ",
	    "HLT_TripleMu_12_10_5",
	    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
	    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
	    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8",
	    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8"
            ]

# MET Filters (AND Logic)
MET_FILTERS = [
    "Flag_goodVertices",
    "Flag_globalSuperTightHalo2016Filter",
    "Flag_EcalDeadCellTriggerPrimitiveFilter",
    "Flag_BadPFMuonFilter",
    "Flag_BadPFMuonDzFilter",
    "Flag_hfNoisyHitsFilter",
    "Flag_eeBadScFilter",
    "Flag_ecalBadCalibFilter"
]

BRANCHES_TO_SAVE = [
    "PV_ndof",
    "PV_x",
    "PV_y",
    "PV_z",
    "PV_chi2",
    "PV_npvs",
    "PV_npvsGood",

    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu37_Ele27_CaloIdL_MW",
    "HLT_Mu27_Ele37_CaloIdL_MW",
    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ",
    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL",
    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ",
    "HLT_Ele28_eta2p1_WPTight_Gsf_HT150",
    "HLT_Ele30_WPTight_Gsf",
    "HLT_Ele32_WPTight_Gsf",
    "HLT_Ele35_WPTight_Gsf",
    "HLT_Ele38_WPTight_Gsf",
    "HLT_Ele40_WPTight_Gsf",
    "HLT_Ele115_CaloIdVT_GsfTrkIdT",
    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_DoubleEle33_CaloIdL_MW",
    "HLT_DoubleEle25_CaloIdL_MW",
    "HLT_DoubleEle27_CaloIdL_MW",
    "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL",
    "HLT_IsoMu24",
    "HLT_IsoMu24_eta2p1",
    "HLT_IsoMu27",
    "HLT_IsoMu50_AK8PFJet230_SoftDropMass40",
    "HLT_TripleMu_10_5_5_DZ",
    "HLT_TripleMu_12_10_5",
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8",
    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8",

    "Flag_goodVertices",
    "Flag_globalSuperTightHalo2016Filter",
    "Flag_EcalDeadCellTriggerPrimitiveFilter",
    "Flag_BadPFMuonFilter",
    "Flag_BadPFMuonDzFilter",
    "Flag_hfNoisyHitsFilter",
    "Flag_eeBadScFilter",
    "Flag_ecalBadCalibFilter",


    # Event
    "run",
    "event",
    "luminosityBlock",

    # MET
    "PuppiMET_pt",
    "PuppiMET_phi",

    # MC-only (if isMC)
#    "Pileup_nPU",
#    "Pileup_nTrueInt",
#    "Generator_weight",
#    "GenMET_pt",
#    "GenMET_phi",

    # Object counts
    "nElectron",
    "nMuon",
    "nJet",
    "Rho_fixedGridRhoFastjetAll"
    # Gen-level (MC only)
#    "nGenPart",
#    "nLHEPart",
#    "nGenJet",
#    "nPSWeight",
#    "PSWeight",
#    "nLHEPdfWeight",
#    "LHEPdfWeight",
#    "nLHEScaleWeight",
#    "LHEScaleWeight",
#    "LHEWeight_originalXWGTUP",
#    "Rho_fixedGridRhoFastjetAll"
]

BRANCHES_MC = [

    # Pileup + generator
    "Pileup_nPU",
    "Pileup_nTrueInt",
    "genWeight",
    "GenMET_pt",
    "GenMET_phi",

    # Gen-level
    "nGenPart",
    "nLHEPart",
    "nGenJet",
    "nPSWeight",
    "PSWeight",
    "nLHEPdfWeight",
    "LHEPdfWeight",
    "nLHEScaleWeight",
    "LHEScaleWeight",
    "LHEWeight_originalXWGTUP",
]

BRANCHES_WILDCARD = [
    "Electron_*",
    "Muon_*",
    "Jet_*",
    "GenPart_*",
    "LHEPart_*",
    "GenJet_*"
]

BRANCHES_WILDCARD_DATA = [
    "Electron_*",
    "Muon_*",
    "Jet_*"
]

