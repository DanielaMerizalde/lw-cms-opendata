#!/bin/bash
# Usage: ./run_sample.sh M SEED
# LHE (mg5/PROC_lw_ejj/Events/M$M) -> Pythia8 (causal HepMC2 + truth CSV) -> reflection (acausal HepMC2) -> checks
set -e
M=$1; SEED=$2
HERE=$(cd "$(dirname "$0")" && pwd)
PY=/Users/danielamerizalde/miniforge3/bin/python3
case $M in 200) CT=0.0270765;; 300) CT=0.0164300;; 400) CT=0.0121212;; 500) CT=0.00965243;; esac
OUT=$HERE/samples/M$M; mkdir -p $OUT
cp $HERE/mg5/PROC_lw_ejj/Events/M$M/unweighted_events.lhe.gz $OUT/lw_M${M}.lhe.gz
cp $HERE/mg5/PROC_lw_ejj/Events/M$M/M${M}_tag_1_banner.txt $OUT/lw_M${M}_mg5_banner.txt
$HERE/pythia/lw_pythia_hepmc $HERE/pythia/lw_8TeV_CUETP8M1.cmnd $OUT/lw_M${M}.lhe.gz $OUT/lw_M${M}_causal $M $CT $SEED > $OUT/pythia_M${M}.log 2>&1
grep LWSUMMARY $OUT/pythia_M${M}.log
mv $OUT/lw_M${M}_causal_elw.csv $OUT/truth_M${M}_elw.csv
mv $OUT/lw_M${M}_causal_jets.csv $OUT/truth_M${M}_jets.csv
$PY $HERE/tools/lw_reflect_hepmc.py $OUT/lw_M${M}_causal.hepmc $OUT/lw_M${M}_acausal.hepmc | tee $OUT/reflect_M${M}.log
$PY $HERE/tools/hepmc_vertex_check.py $OUT/lw_M${M}_causal.hepmc $OUT/lw_M${M}_acausal.hepmc | tee $OUT/vertexcheck_M${M}.log
gzip -f -6 $OUT/lw_M${M}_causal.hepmc &
gzip -f -6 $OUT/lw_M${M}_acausal.hepmc &
wait
ls -la $OUT
