#!/bin/bash
# Host-side scheduler: runs all chunk jobs (causal and acausal, 50 events each) with at most NPAR containers at once.
# Usage: cmssw/launch_production.sh NPAR [PU=1]      (run with nohup from phase3/signal)
# Chunk k (events 50k..50k+49) uses FIRST=50k+1 and SEED=1000+k for BOTH versions (common random numbers).
# Skips chunks whose AODSIM already exists. Job containers: lw3a-<version>-<k>.
NPAR=${1:-3}; PU=${2:-1}
SIG=$(cd "$(dirname "$0")/.." && pwd)
IMG=cmsopendata/cmssw_5_3_32:latest
jobs=()
for k in $(seq 0 39); do for v in causal acausal; do jobs+=("$v $k"); done; done
for j in "${jobs[@]}"; do
  set -- $j; v=$1; k=$2; tag=$(printf 'c%03d' $k)
  [ -f $SIG/aod/$v/lw_zonly_M200_${v}_${tag}_AODSIM.root ] && continue
  docker ps -q --filter name=^lw3a-$v-$tag$ | grep -q . && continue   # already running
  [ -f $SIG/cmssw/NPAR ] && NPAR=$(cat $SIG/cmssw/NPAR)   # can be changed while running
  while [ $(docker ps --filter name=lw3a-causal- --filter name=lw3a-acausal- -q | wc -l) -ge $NPAR ]; do sleep 30; [ -f $SIG/cmssw/NPAR ] && NPAR=$(cat $SIG/cmssw/NPAR); done
  docker rm lw3a-$v-$tag >/dev/null 2>&1
  docker run -d --memory 2g --platform linux/amd64 --name lw3a-$v-$tag -v $SIG:/work -e LW_PU=$PU $IMG \
     /work/cmssw/run_chunk.sh $v /work/hepmc_chunks/$v/$(printf 'chunk_%03d' $k).hepmc $((50*k+1)) $((1000+k)) $tag 0 -1 >/dev/null
  echo "$(date '+%F %T') started $v $tag"
  sleep 20
done
echo "$(date '+%F %T') all jobs submitted"
