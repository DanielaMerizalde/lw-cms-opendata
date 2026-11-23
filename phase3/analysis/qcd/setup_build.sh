#!/bin/bash
# Inside the container lwqcd: creates a SEPARATE CMSSW area in /work/qcd/cmssw (the v2 area used by the
# signal production, /work/cmssw, is not touched) and builds WDVQCDAnalyzer.
source /opt/cms/cmsset_default.sh
mkdir -p /work/qcd/cmssw && cd /work/qcd/cmssw
[ -d CMSSW_5_3_32 ] || scramv1 project CMSSW CMSSW_5_3_32
cd CMSSW_5_3_32/src
[ -e LWQCD ] || ln -s ../../../src/LWQCD LWQCD
eval `scramv1 runtime -sh`
scram b -j4 2>&1 | tail -40
