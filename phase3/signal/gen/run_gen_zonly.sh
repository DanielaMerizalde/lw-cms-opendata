#!/bin/bash
# Phase 3A: Z-only M=200 LHE -> Pythia8 (causal HepMC2 + truth CSV) -> reflection (acausal) -> vertex checks
# Reuses (read-only) generation/events/{pythia,tools}. Same cmnd card/driver as phase 2.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); SIG=$(dirname $HERE)
G=$SIG/../../generation/events
PY=/Users/danielamerizalde/miniforge3/bin/python3
M=200; CT=0.0270765; SEED=${1:-3200}
OUT=$SIG/gen/samples; mkdir -p $OUT
cp $SIG/mg5/PROC_lw_zonly_ejj/Events/M200_zonly/unweighted_events.lhe.gz $OUT/lw_zonly_M200.lhe.gz
cp $SIG/mg5/PROC_lw_zonly_ejj/Events/M200_zonly/M200_zonly_tag_1_banner.txt $OUT/lw_zonly_M200_mg5_banner.txt
$G/pythia/lw_pythia_hepmc $G/pythia/lw_8TeV_CUETP8M1.cmnd $OUT/lw_zonly_M200.lhe.gz $OUT/lw_zonly_M200_causal $M $CT $SEED > $OUT/pythia_zonly_M200.log 2>&1
grep LWSUMMARY $OUT/pythia_zonly_M200.log
mv $OUT/lw_zonly_M200_causal_elw.csv $OUT/truth_M200_elw.csv
mv $OUT/lw_zonly_M200_causal_jets.csv $OUT/truth_M200_jets.csv
$PY $G/tools/lw_reflect_hepmc.py $OUT/lw_zonly_M200_causal.hepmc $OUT/lw_zonly_M200_acausal.hepmc | tee $OUT/reflect_zonly_M200.log
$PY $G/tools/hepmc_vertex_check.py $OUT/lw_zonly_M200_causal.hepmc $OUT/lw_zonly_M200_acausal.hepmc | tee $OUT/vertexcheck_zonly_M200.log
ls -la $OUT
