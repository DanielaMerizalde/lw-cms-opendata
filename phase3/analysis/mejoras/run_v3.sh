#!/bin/bash
# inside lw3b-sig: run_v3.sh <filelist> <out.root> [maxEvents]
source /opt/cms/cmsset_default.sh
cd /work/mejoras/cmssw/CMSSW_5_3_32/src && eval `scramv1 runtime -sh`; cd /work/mejoras
exec cmsRun /work/mejoras/src/LWv3/WDVv3/python/wdv3_cfg.py fileList=$1 out=$2 maxEvents=${3:--1}
