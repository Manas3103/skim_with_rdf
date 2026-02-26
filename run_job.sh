#!/bin/bash

process=$1
part=$2

echo "======================================"
echo "Process: ${process}"
echo "Part:    ${part}"
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
    cd -

    echo "System Info"
    date
    uname -a
    cat /etc/redhat-release
fi

echo "Running python skimmer..."

python3 runner.py ${process} ${part}

outputdir="root://cmseos.fnal.gov//store/user/msahoo/2024"

if [ -n "${_CONDOR_SCRATCH_DIR}" ]; then
    echo "Copying output to EOS"
    xrdcp -f ${process}_${part}.root ${outputdir}/
    echo "Cleanup"
    rm -rf CMSSW_13_3_3
    rm *.root
fi

echo "Job finished."

