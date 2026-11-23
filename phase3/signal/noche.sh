#!/bin/bash
# noche.sh — producción nocturna desatendida de la señal sólo-Z (M = 200 GeV) en bloques de 25 eventos.
#
# Uso (desde cualquier carpeta):   nohup ~/Downloads/lee-wick/lw-cms-opendata/phase3/signal/noche.sh [HORA_LIMITE] [NPAR] &
#   HORA_LIMITE  hora (HH:MM) antes de la cual deben terminar todos los bloques de la noche (por defecto 07:30)
#   NPAR         bloques simultáneos (por defecto 3; cada contenedor usa hasta 2 GB de RAM)
# Variables opcionales:  DRY=1  sólo muestra lo que haría (no lanza nada ni duerme la Mac)
#                        NO_SLEEP=1  no poner la Mac en reposo al final
#
# Qué hace:
#   1. Evita que la Mac se duerma mientras trabaja (caffeinate) y abre Docker si está cerrado.
#   2. Recorre los 40 bloques (20 causales + 20 acausales, b000..b019), se salta los que ya tienen su AODSIM
#      y lanza hasta NPAR a la vez. Sólo empieza un bloque si se estima que termina antes de HORA_LIMITE.
#   3. Un bloque que falla se reintenta (máx. 3 intentos en total, contados entre noches).
#   4. Cuando ya no cabe ningún bloque y no queda ninguno corriendo: escribe un resumen, cierra Docker
#      y pone la Mac en reposo (pmset sleepnow).
# El bloque k usa los eventos 25k+1..25k+25 y la semilla 2000+k en ambas versiones (números aleatorios comunes).

DEADLINE=${1:-07:30}; NPAR=${2:-3}
SIG=$(cd "$(dirname "$0")" && pwd)
IMG=cmsopendata/cmssw_5_3_32:latest
NBLK=20; NPER=25
STATE=$SIG/state; LOGD=$SIG/logs/noche; mkdir -p $STATE $LOGD
LOG=$LOGD/noche_$(date +%Y%m%d_%H%M).log
DEFAULT_EST=10800          # 3 h por bloque mientras no haya bloques terminados que medir
MARGIN=1.15                # margen de seguridad sobre la duración medida

log() { echo "$(date '+%F %T')  $*" | tee -a "$LOG"; }

# --- no dormir mientras el script vive (sólo con corriente; la tapa debe quedar abierta) ---
if [ -z "$DRY" ] && [ -z "$LW_CAFFEINATED" ]; then
  export LW_CAFFEINATED=1
  exec caffeinate -i -s "$0" "$@"
fi

# --- hora límite (próxima ocurrencia de HH:MM) ---
now=$(date +%s)
dl=$(date -j -f "%Y-%m-%d %H:%M" "$(date +%F) $DEADLINE" +%s)
[ "$dl" -le "$now" ] && dl=$((dl + 86400))
log "inicio. hora límite $(date -r $dl '+%F %H:%M'), NPAR=$NPAR, DRY=${DRY:-0}"

# --- Docker ---
if [ -z "$DRY" ]; then
  if ! docker info >/dev/null 2>&1; then
    log "abriendo Docker…"; open -a Docker
    for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 10; done
    docker info >/dev/null 2>&1 || { log "ERROR: Docker no arrancó en 10 min. Me detengo."; exit 1; }
  fi
  # borra contenedores de bloques ya terminados o abortados (sólo los de este script: lw3a-*-bNNN)
  for c in $(docker ps -a --filter status=exited --filter status=created --format '{{.Names}}' | grep -E '^lw3a-(causal|acausal)-b[0-9]{3}$'); do
    docker rm "$c" >/dev/null
  done
fi

aod()     { echo "$SIG/aod/$1/lw_zonly_M200_$1_$2_AODSIM.root"; }
running() { [ -n "$DRY" ] && { echo 0; return; }; docker ps --format '{{.Names}}' | grep -cE '^lw3a-(causal|acausal)-b[0-9]{3}$'; }
is_running() { [ -z "$DRY" ] && docker ps --format '{{.Names}}' | grep -qx "lw3a-$1-$2"; }

est_block() {   # duración estimada de un bloque (s), a partir de los bloques ya terminados
  local t
  t=$(cat $SIG/logs/cmssw/*/b[0-9][0-9][0-9]_timing.txt 2>/dev/null | sed -n 's/.*total=\([0-9]*\)s.*/\1/p' \
      | awk -v m=$MARGIN '{s+=$1;n++} END{if(n) printf "%d", m*s/n}')
  echo "${t:-$DEFAULT_EST}"
}

pending_list() {  # "version k" de los bloques sin AODSIM, alternando causal/acausal
  for k in $(seq 0 $((NBLK-1))); do
    tag=$(printf 'b%03d' $k)
    for v in causal acausal; do
      [ -f "$(aod $v $tag)" ] && continue
      echo "$v $k"
    done
  done
}

launch() {  # $1 version, $2 k
  local v=$1 k=$2 tag; tag=$(printf 'b%03d' $k)
  local af=$STATE/attempts_${v}_$tag; local n=$(cat $af 2>/dev/null || echo 0)
  if [ "$n" -ge 3 ]; then return 1; fi
  if [ -n "$DRY" ]; then log "[DRY] lanzaría $v $tag (intento $((n+1)))"; return 0; fi
  echo $((n+1)) > $af
  docker rm "lw3a-$v-$tag" >/dev/null 2>&1
  docker run -d --memory 2g --platform linux/amd64 --name "lw3a-$v-$tag" -v "$SIG":/work -e LW_PU=1 $IMG \
    /work/cmssw/run_chunk.sh $v /work/hepmc_chunks25/$v/$(printf 'chunk_%03d' $k).hepmc $((NPER*k+1)) $((2000+k)) $tag 0 -1 >/dev/null \
    && log "lanzado $v $tag (intento $((n+1)))" || { log "ERROR al lanzar $v $tag"; return 1; }
}

done_before=$(ls $SIG/aod/causal/*_b[0-9][0-9][0-9]_AODSIM.root $SIG/aod/acausal/*_b[0-9][0-9][0-9]_AODSIM.root 2>/dev/null | wc -l | tr -d ' ')
log "bloques ya terminados antes de esta noche: $done_before/$((2*NBLK))"

# --- bucle principal ---
while :; do
  est=$(est_block); now=$(date +%s); r=$(running); launched=0
  if [ $((now + est)) -lt "$dl" ]; then
    while read -r v k; do
      [ -z "$v" ] && continue
      [ "$r" -ge "$NPAR" ] && break
      is_running $v $(printf 'b%03d' $k) && continue
      launch $v $k && { r=$((r+1)); launched=1; [ -z "$DRY" ] && sleep 20; }
    done < <(pending_list)
  fi
  [ -n "$DRY" ] && { log "[DRY] estimación por bloque: $((est/60)) min"; break; }
  r=$(running)
  if [ "$r" -eq 0 ] && [ "$launched" -eq 0 ]; then break; fi
  sleep 60
done

# --- resumen ---
done_after=$(ls $SIG/aod/causal/*_b[0-9][0-9][0-9]_AODSIM.root $SIG/aod/acausal/*_b[0-9][0-9][0-9]_AODSIM.root 2>/dev/null | wc -l | tr -d ' ')
failed=$(for f in $STATE/attempts_*; do [ -f "$f" ] && [ "$(cat $f)" -ge 3 ] && b=${f#$STATE/attempts_} && [ ! -f "$(aod ${b%_*} ${b##*_})" ] && echo ${b}; done 2>/dev/null | tr '\n' ' ')
log "RESUMEN: esta noche se terminaron $((done_after - done_before)) bloques; total $done_after/$((2*NBLK))."
[ -n "$failed" ] && log "ATENCIÓN: bloques que fallaron 3 veces (revisar logs/cmssw): $failed"
[ "$done_after" -ge $((2*NBLK)) ] && log "¡Producción completa! Ya se puede correr el análisis sobre la señal."
grep -h "DONE" $SIG/logs/cmssw/*/b[0-9][0-9][0-9]_timing.txt 2>/dev/null | tail -n 6 >> "$LOG"

[ -n "$DRY" ] && exit 0
# --- cerrar Docker y dormir la Mac ---
log "cerrando Docker"
osascript -e 'quit app "Docker"' >/dev/null 2>&1 || osascript -e 'quit app "Docker Desktop"' >/dev/null 2>&1
sleep 30
if [ -z "$NO_SLEEP" ]; then log "poniendo la Mac en reposo"; pmset sleepnow; fi
