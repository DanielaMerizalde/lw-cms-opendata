#!/bin/bash
# inside container: run_v3final.sh <isData> <filelist> <out.root> [maxEvents]   (v3 final: cleaning 0 + AVF)
source /opt/cms/cmsset_default.sh
cd /work/mejoras/cmssw/CMSSW_5_3_32/src && eval `scramv1 runtime -sh`; cd /work/mejoras
J=""; [ "$1" = "1" ] && J="json=/work/data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"
exec cmsRun /work/mejoras/src/LWv3/WDVv3/python/wdv3_cfg.py isData=$1 fileList=$2 out=$3 maxEvents=${4:--1} final=1 $J
