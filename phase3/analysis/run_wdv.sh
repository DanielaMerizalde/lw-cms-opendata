#!/bin/bash
# Usage (inside container): run_wdv.sh <isData 0/1> <filelist> <out.root> [maxEvents] [extra args]
source /opt/cms/cmsset_default.sh
cd /work/cmssw/CMSSW_5_3_32/src && eval `scramv1 runtime -sh`
ISDATA=$1; FL=$2; OUT=$3; MAXEV=${4:--1}; shift 4
if [ "$ISDATA" = "1" ]; then
  CONN=sqlite_file:/opt/cms-opendata-conddb/FT53_V21A_AN6_FULL_data_stripped.db
  EXTRA="json=/work/data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt globalTag=FT53_V21A_AN6_FULL"
else
  CONN=sqlite_file:/opt/cms-opendata-conddb/START53_V27_MC_stripped.db
  EXTRA="globalTag=START53_V27"
fi
cd /work
exec cmsRun /work/src/LWAnalysis/WDVAnalyzer/python/wdv_cfg.py isData=$ISDATA fileList=$FL out=$OUT maxEvents=$MAXEV gtConnect=$CONN $EXTRA "$@"
