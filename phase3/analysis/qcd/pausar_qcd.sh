#!/bin/bash
# pausar_qcd.sh "YYYY-MM-DD HH:MM" — detiene limpiamente lanzar_todos.sh a esa hora (lo terminado queda guardado).
# Reanudar: nohup caffeinate -i -s ./lanzar_todos.sh 5 >> lanzar_todos.log 2>&1 &
cd "$(dirname "$0")"
T=$(date -j -f "%Y-%m-%d %H:%M" "$1" +%s) || exit 1
echo "$(date '+%F %T') pausa programada para $1" >> pausar_qcd.log
while [ $(date +%s) -lt $T ]; do pgrep -qf lanzar_todos.sh || { echo "$(date '+%F %T') ya no corría; nada que pausar" >> pausar_qcd.log; exit 0; }; sleep 30; done
pkill -f lanzar_todos.sh; pkill -f "prod_qcd.py --njobs"; sleep 2
docker stop lwqcd >/dev/null 2>&1
rm -f out/*/*.tmp.root
echo "pausado: $(date)  ($(sort -u done/data.txt 2>/dev/null | wc -l | tr -d ' ') archivos de datos listos)" | tee -a lanzar_todos.log >> pausar_qcd.log
