#!/bin/bash

process=$1
part=$2
jobtype=$3

echo "======================================"
echo "Process: ${process}"
echo "Part:    ${part}"
echo "jobtype:    ${jobtype}"
echo "======================================"

if [ -z ${_CONDOR_SCRATCH_DIR} ] ; then
    echo "Running Interactively"
else
    echo "Running In Batch"
    cd ${_CONDOR_SCRATCH_DIR}
    echo "Scratch dir: ${_CONDOR_SCRATCH_DIR}"

    source /cvmfs/cms.cern.ch/cmsset_default.sh

    export SCRAM_ARCH=el9_amd64_gcc12
    scramv1 project CMSSW CMSSW_13_3_3
    cd CMSSW_13_3_3/src
    cmsenv
    eval `scramv1 runtime -sh`
    cd ${_CONDOR_SCRATCH_DIR}

#     echo "=== FILES AFTER TRANSFER ==="
#     pwd
#     ls -al

    echo "System Info"
    date
    uname -a
    cat /etc/redhat-release
fi

echo "Running python skimmer..."

python3 runner.py ${process} ${part}

base="root://cmseos.fnal.gov//store/user/msahoo/2024"

# Decide output directory
if [ "$jobtype" == "DATA" ]; then
    outputdir="${base}/DATA_Skimmed/${process}"
    eosdir="/store/user/msahoo/2024/DATA_Skimmed/${process}"
else
    outputdir="${base}/${process}"
    eosdir="/store/user/msahoo/2024/${process}"
fi


if [ -n "${_CONDOR_SCRATCH_DIR}" ]; then
    echo "======================================"
    echo "Preparing EOS directory..."
    echo "Job Type: $jobtype"
    echo "Process : $process"
    echo "EOS Dir : $eosdir"
    echo "OUTPUT Dir : $outputdir"
    echo "======================================"
    echo "Checking EOS path accessibility..."

    # xrdfs root://cmseos.fnal.gov ls ${eosdir} > /dev/null 2>&1

    # if [ $? -ne 0 ]; then
	# echo "ERROR: Cannot access EOS path:"
	# echo "xrdfs root://cmseos.fnal.gov ls ${eosdir}"
	# exit 1
    # fi

    # echo "EOS path is accessible." 

    echo "Copying output file to EOS..."
    xrdcp -d 3 -f ${process}_${part}.root ${outputdir}/

    if [ $? -eq 0 ]; then
        echo "File successfully copied to ${outputdir}"
    else
        echo "ERROR: xrdcp failed!"
        exit 1
    fi

    echo "Cleanup..."
    rm -rf CMSSW_13_3_3
    rm -f *.root
fi

echo "Job finished."
