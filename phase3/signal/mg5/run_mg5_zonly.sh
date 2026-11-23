#!/bin/bash
# Usage: ./run_mg5_zonly.sh PROCDIR RUNNAME NEVENTS SEED
# Same run_card settings as generation/events/mg5/run_mg5.sh (phase 2), param_card_M200 (etaLW=+1, lwRep=0, MeLW=5e-4, WLW=7.28775e-12)
set -e
PROC=$1; RUN=$2; N=$3; SEED=$4
HERE=$(cd "$(dirname "$0")" && pwd)
MG5=/Users/danielamerizalde/Downloads/lee-wick/MG5_aMC_v3_8_1/bin/mg5_aMC
cat > $HERE/cards/launch_${RUN}.mg5 <<EOC
launch $HERE/$PROC -n $RUN
shower=OFF
madspin=OFF
analysis=OFF
done
$HERE/cards/param_card_M200.dat
set nevents $N
set iseed $SEED
set ebeam1 4000
set ebeam2 4000
set time_of_flight 0.0
set use_syst False
set ptj 0
set ptl 0
set ptb 0
set etaj -1
set etal -1
set etab -1
set drjj 0
set drll 0
set drjl 0
set drbb 0
set drbj 0
set drbl 0
set cut_decays False
done
EOC
$MG5 $HERE/cards/launch_${RUN}.mg5 > $HERE/logs/mg5_${RUN}.log 2>&1
grep -i "cross-section\|Nb of events" $HERE/logs/mg5_${RUN}.log | tail -3
