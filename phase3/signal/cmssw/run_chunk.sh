#!/bin/bash
# Inside cmsopendata/cmssw_5_3_32 (entrypoint has done cmsenv). /work = phase3/signal on the host.
# Usage: run_chunk.sh VERSION(causal|acausal) HEPMC_IN FIRST_EVENT SEED TAG [KEEP_INTERMEDIATE=0] [NEVENTS=-1]
# GEN-SIM -> DIGI-L1-DIGI2RAW-HLT(7E33v2, PU per LW_PU) -> RECO(AODSIM). Seed identical for causal/acausal.
set -o pipefail
V=$1; IN=$2; FIRST=$3; SEED=$4; TAG=$5; KEEP=${6:-0}; N=${7:--1}
W=/work/work/$V/$TAG; L=/work/logs/cmssw/$V; A=/work/aod/$V
mkdir -p $W $L $A
cd /work/cmssw/CMSSW_5_3_32/src && eval `scramv1 runtime -sh` && cd $W   # persistent area with the LWMCFileSource plugin
export LW_N=$N LW_FIRST=$FIRST LW_SEED=$SEED
t0=$(date +%s)
LW_IN=$IN LW_OUT=$W/gensim.root cmsRun /work/cmssw/cfg/gensim_cfg.py > $L/${TAG}_gensim.log 2>&1 || { echo "FAIL gensim $V $TAG"; exit 1; }
t1=$(date +%s)
LW_IN=$W/gensim.root LW_OUT=$W/hlt.root cmsRun /work/cmssw/cfg/hlt_cfg.py > $L/${TAG}_hlt.log 2>&1 || { echo "FAIL hlt $V $TAG"; exit 2; }
t2=$(date +%s)
LW_IN=$W/hlt.root LW_OUT=$W/aodsim.root cmsRun /work/cmssw/cfg/reco_cfg.py > $L/${TAG}_reco.log 2>&1 || { echo "FAIL reco $V $TAG"; exit 3; }
t3=$(date +%s)
mv $W/aodsim.root $A/lw_zonly_M200_${V}_${TAG}_AODSIM.root
echo "DONE $V $TAG gensim=$((t1-t0))s hlt=$((t2-t1))s reco=$((t3-t2))s total=$((t3-t0))s" | tee -a $L/${TAG}_timing.txt
[ "$KEEP" = 1 ] || rm -rf $W
