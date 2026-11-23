#!/bin/bash
# vigilar.sh — shows the progress of the signal production (produccion_2000.sh); refreshes every 30 s.
# Only reads; it never touches the containers.   Usage: ./vigilar.sh      (Ctrl-C to quit)
SIG=$(cd "$(dirname "$0")" && pwd)
L=$SIG/logs/cmssw/causal
while true; do
  clear
  echo "=== Producción Lee–Wick causal — $(date '+%H:%M:%S') ==="
  pmset -g batt | sed -n 2p | sed 's/^ *-InternalBattery-0 ([^)]*)/Batería:/'
  pgrep -q caffeinate && echo "Mac sin dormirse: sí (caffeinate activo)" || echo "Mac sin dormirse: NO — ¡ojo!"
  echo
  echo "--- Bloques en marcha (cada bloque = 50 colisiones; pasos GEN-SIM → HLT → RECO) ---"
  for c in $(docker ps --format '{{.Names}}' | grep -E '^lw3c-causal-b[0-9]{3}$' | sort); do
    b=${c##*-}
    if   [ -f $L/${b}_reco.log ]; then st="3/3 RECO   "; f=$L/${b}_reco.log
    elif [ -f $L/${b}_hlt.log ];  then st="2/3 HLT    "; f=$L/${b}_hlt.log
    elif [ -f $L/${b}_gensim.log ]; then st="1/3 GEN-SIM"; f=$L/${b}_gensim.log
    else st="arrancando "; f=; fi
    n=0; [ -n "$f" ] && n=$(grep -c "Begin processing" "$f")
    cpu=$(docker stats --no-stream --format '{{.CPUPerc}}' $c 2>/dev/null)
    up=$(docker ps --filter name=^$c$ --format '{{.RunningFor}}')
    printf "  %s  paso %s  colisión %2d/50   CPU %7s   (lleva %s)\n" "$b" "$st" "$n" "$cpu" "$up"
  done
  docker ps --format '{{.Names}}' | grep -qE '^lw3c-causal' || echo "  (ninguno ahora mismo)"
  echo
  done_n=$(ls $SIG/aod/causal/lw_zonly_M200_causal_b0[2-5][0-9]_AODSIM.root 2>/dev/null | wc -l | tr -d ' ')
  echo "--- Bloques nuevos terminados: $done_n de 40 (b020–b059) ---"
  ls -t $SIG/aod/causal/lw_zonly_M200_causal_b0[2-5][0-9]_AODSIM.root 2>/dev/null | head -5 | sed 's|.*/|  |'
  echo
  echo "(se actualiza cada 30 s · Ctrl-C para cerrar esta ventana; la producción sigue)"
  sleep 30
done
