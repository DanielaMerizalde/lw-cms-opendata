#!/bin/bash
# vigilar_todos.sh — progreso de lanzar_todos.sh (todos los datos). Solo lee. Ctrl-C para cerrar.
cd "$(dirname "$0")"
while true; do
  clear
  echo "=== QCD con todos los datos — $(date '+%a %H:%M') ==="
  pgrep -q caffeinate && echo "Mac sin dormirse: sí" || echo "Mac sin dormirse: NO"
  if pgrep -qf prod_qcd.py; then echo "Estado: procesando archivos (paso 1 de 2)"
  elif pgrep -qf qcd_desde_datos.py; then echo "Estado: calculando QCD (paso 2 de 2)"
  elif tail -1 lanzar_todos.log 2>/dev/null | grep -q "^fin:"; then echo "Estado: TERMINADO — resultados en qcd/plots/"
  else echo "Estado: detenido (ver lanzar_todos.log)"; fi
  tot=$(ls lists_full/data | wc -l | tr -d ' '); d=$(sort -u done/data.txt 2>/dev/null | wc -l | tr -d ' ')
  printf "\nDatos: %d de %d archivos (%.1f %%)\n" $d $tot $(echo "100*$d/$tot" | bc -l)
  t0=$(stat -f %B lanzar_todos.log 2>/dev/null); ok=$(grep -c " OK data/" lanzar_todos.log 2>/dev/null)
  if [ -n "$t0" ] && [ "$ok" -gt 0 ]; then
    el=$(( $(date +%s) - t0 )); rest=$(( el * (tot - d) / ok ))
    printf "Esta corrida: %d archivos en %dh%02dm → faltan ~%dd %dh (hacia el %s)\n" $ok $((el/3600)) $((el%3600/60)) \
      $((rest/86400)) $((rest%86400/3600)) "$(date -r $(( $(date +%s) + rest )) '+%a %d %H:%M')"
    echo "(la estimación se afina con las horas; la velocidad de la red del CERN cambia mucho)"
  fi
  [ -s done/failed.txt ] && echo "Fallidos: $(wc -l < done/failed.txt | tr -d ' ') (se pueden reintentar al final)"
  echo; echo "Últimos terminados:"; grep " OK data/" lanzar_todos.log 2>/dev/null | tail -3 | cut -c1-60
  echo; echo "(se actualiza cada 60 s · Ctrl-C cierra esta ventana; el análisis sigue)"
  sleep 60
done
