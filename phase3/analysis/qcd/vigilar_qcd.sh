#!/bin/bash
# vigilar_qcd.sh — muestra el progreso del análisis QCD (lanzar_todo.sh); se actualiza cada 30 s.
# Solo lee; no toca el proceso.   Uso: ./vigilar_qcd.sh      (Ctrl-C para cerrar; el análisis sigue)
Q=$(cd "$(dirname "$0")" && pwd)
cd "$Q"
T0=$(stat -f %B lanzar_todo.log 2>/dev/null)   # creation time of the log = start of lanzar_todo.sh
while true; do
  clear
  echo "=== Análisis QCD desde datos — $(date '+%H:%M:%S') ==="
  pgrep -q caffeinate && echo "Mac sin dormirse: sí" || echo "Mac sin dormirse: NO — ¡ojo!"
  if pgrep -qf prod_qcd.py; then echo "Estado: procesando archivos (paso 1 de 2)"
  elif pgrep -qf qcd_desde_datos.py; then echo "Estado: calculando QCD (paso 2 de 2)"
  elif grep -q "^fin:" lanzar_todo.log 2>/dev/null; then echo "Estado: TERMINADO — resultados en qcd/plots/"
  else echo "Estado: detenido (ver lanzar_todo.log)"; fi
  echo
  echo "--- Archivos terminados por muestra ---"
  tot=0; hech=0
  for s in DY TT W1 W2 W3 data; do
    n=$(ls ../lists/$s/*.txt 2>/dev/null | wc -l | tr -d ' ')
    d=$(cat done/$s.txt 2>/dev/null | wc -l | tr -d ' ')
    tot=$((tot+n)); hech=$((hech+d))
    printf "  %-5s %3d / %3d\n" "$s" "$d" "$n"
  done
  printf "  TOTAL %3d / %3d\n" "$hech" "$tot"
  echo
  echo "--- Archivos en proceso ahora ---"
  for f in $(ls out/*/*.tmp.root 2>/dev/null); do
    s=$(basename $(dirname $f)); b=$(basename $f .tmp.root)
    ev=$(grep -o "Begin processing the [0-9]*" logs/$s/$b.log 2>/dev/null | tail -1 | grep -o "[0-9]*$")
    printf "  %-5s %s  evento %s\n" "$s" "${b:0:20}…" "${ev:-arrancando}"
  done
  ls out/*/*.tmp.root >/dev/null 2>&1 || {
    for l in $(ls -t logs/*/*.log 2>/dev/null | head -4); do
      s=$(basename $(dirname $l)); b=$(basename $l .log)
      grep -q "^$b$" done/$s.txt 2>/dev/null && continue
      ev=$(grep -o "Begin processing the [0-9]*" $l | tail -1 | grep -o "[0-9]*$")
      printf "  %-5s %s  evento %s\n" "$s" "${b:0:20}…" "${ev:-arrancando}"
    done; }
  echo
  if [ -n "$T0" ] && [ "$hech" -gt 0 ]; then
    el=$(( $(date +%s) - T0 )); rest=$(( el * (tot - hech) / hech ))
    printf "Llevamos %dh%02dm. Estimación para terminar: ~%dh%02dm (hacia las %s)\n" $((el/3600)) $((el%3600/60)) \
      $((rest/3600)) $((rest%3600/60)) "$(date -r $(( $(date +%s) + rest )) '+%H:%M')"
    echo "(los primeros archivos son MC, más pequeños: la estimación se afina con los de datos)"
  fi
  [ -s done/failed.txt ] && { echo; echo "--- FALLIDOS ---"; cat done/failed.txt; }
  echo
  echo "(se actualiza cada 30 s · Ctrl-C para cerrar esta ventana; el análisis sigue)"
  sleep 30
done
