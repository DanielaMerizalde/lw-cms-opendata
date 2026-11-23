#!/bin/bash
source /opt/cms/cmsset_default.sh
mkdir -p /work/mejoras/cmssw && cd /work/mejoras/cmssw
[ -d CMSSW_5_3_32 ] || scramv1 project CMSSW CMSSW_5_3_32
cd CMSSW_5_3_32/src; [ -e LWv3 ] || ln -s ../../../src/LWv3 LWv3
eval `scramv1 runtime -sh`; scram b -j6 2>&1 | grep -E "error|Error|built" | head -30
