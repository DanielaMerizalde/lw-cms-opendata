#!/bin/bash
# Run inside the lw3b container: creates CMSSW area in /work/cmssw and builds the analyzer.
source /opt/cms/cmsset_default.sh
mkdir -p /work/cmssw && cd /work/cmssw
[ -d CMSSW_5_3_32 ] || scramv1 project CMSSW CMSSW_5_3_32
cd CMSSW_5_3_32/src
[ -e LWAnalysis ] || ln -s ../../../src/LWAnalysis LWAnalysis
eval `scramv1 runtime -sh`
scram b -j4 2>&1 | tail -40
