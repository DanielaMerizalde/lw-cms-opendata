#!/bin/bash
# Inside the container lwqcd: run_qcd.sh <isData 0/1> <filelist> <out.root> [maxEvents] [cacheBytes|""] [extra key=value ...]
source /opt/cms/cmsset_default.sh
cd /work/qcd/cmssw/CMSSW_5_3_32/src && eval `scramv1 runtime -sh`
ISDATA=$1; FL=$2; OUT=$3; MAXEV=${4:--1}; CACHE=${5:-}; shift 5 2>/dev/null || shift $#
if [ "$ISDATA" = "1" ]; then
  CONN=sqlite_file:/opt/cms-opendata-conddb/FT53_V21A_AN6_FULL_data_stripped.db
  EXTRA="json=/work/data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt globalTag=FT53_V21A_AN6_FULL"
else
  CONN=sqlite_file:/opt/cms-opendata-conddb/START53_V27_MC_stripped.db
  EXTRA="globalTag=START53_V27"
fi
cd /work/qcd
exec cmsRun /work/qcd/src/LWQCD/WDVQCD/python/wdvqcd_cfg.py isData=$ISDATA fileList=$FL out=$OUT maxEvents=$MAXEV gtConnect=$CONN $EXTRA ${CACHE:+cache=$CACHE} "$@"
