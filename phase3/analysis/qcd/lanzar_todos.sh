#!/bin/bash
# lanzar_todos.sh — QCD con TODOS los datos 2012 (4331 archivos, 11.5 fb^-1). Se salta lo ya hecho.
# Corre WDVQCDAnalyzer archivo por archivo (prod_qcd.py) en modo rápido lazyHQ=1: lee lo liviano de cada colisión y
# las trazas/partículas solo de las ~9 por archivo que llegan a los vértices (árbol events idéntico; el árbol elA
# queda sin el corte HQ, hq = -1). Luego la luminosidad (lumi_qcd.py) y el cálculo QCD.
# Uso:  nohup caffeinate -i -s ./lanzar_todos.sh [NJOBS] [CACHE] >> lanzar_todos.log 2>&1 &
# Reanudable: si se corta, volver a lanzar el mismo comando.
NJOBS=${1:-4}; CACHE=${2:-}
cd "$(dirname "$0")"
# Una sola corrida a la vez: candado atómico (mkdir) con el PID dentro; un candado de una corrida muerta se reemplaza.
if ! mkdir .lanzar.lock 2>/dev/null; then
  pid=$(cat .lanzar.lock/pid 2>/dev/null)
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then echo "Ya hay una corrida en marcha (pid $pid): no lanzo otra. ($(date))"; exit 0; fi
  rm -rf .lanzar.lock; mkdir .lanzar.lock 2>/dev/null || { echo "Otra corrida tomó el candado: no lanzo otra. ($(date))"; exit 0; }
fi
echo $$ > .lanzar.lock/pid
echo "inicio: $(date)  njobs=$NJOBS cache=${CACHE:-default}"
if ! docker info >/dev/null 2>&1; then echo "abriendo Docker..."; open -a Docker; for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 3; done; fi
docker info >/dev/null 2>&1 || { echo "Docker no arrancó: no lanzo nada."; exit 1; }
docker start lwqcd >/dev/null
python3 prod_qcd.py --njobs $NJOBS --samples DY TT W1 W2 W3 data --listdir lists_full ${CACHE:+--cache $CACHE} --extra lazyHQ=1
docker stop lwqcd >/dev/null
../.venv/bin/python lumi_qcd.py
cd .. && .venv/bin/python qcd/qcd_desde_datos.py
echo "fin: $(date)"
