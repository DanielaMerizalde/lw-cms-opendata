#!/bin/bash
# produccion_2000.sh — 2 000 colisiones NUEVAS de señal Lee–Wick CAUSAL (sólo-Z, M = 200 GeV), misma cadena
# CMSSW_5_3_32 que noche.sh (GEN-SIM -> HLT 7E33v2 con pileup por xrootd -> AODSIM), en bloques de 50 eventos.
#
# Uso:   nohup ~/Downloads/lee-wick/lw-cms-opendata/phase3/signal/produccion_2000.sh [NPAR] [KMIN] [KMAX] > /dev/null 2>&1 &
#   NPAR  bloques simultáneos (por defecto 3). Se puede cambiar en caliente escribiendo un número en state/NPAR_2000.
#   KMIN KMAX  rango de bloques (por defecto 20..59). Útil para la prueba de un solo bloque.
# Variables opcionales: DRY=1 sólo muestra lo que haría.
#
# Bloques (lista en hepmc_chunks50/causal/manifest.txt: "k primer_EventID origen"):
#   b020..b049: eventos 501..2000 de gen/samples/lw_zonly_M200_causal.hepmc.gz (los 1..500 ya están en b000..b019)
#   b050..b059: eventos 1..500 de la muestra nueva gen/samples_ext (MG5 iseed 3301, Pythia seed 3300),
#               con EventID 2001..2500 para no repetir números de evento.
#   Semilla CMSSW del bloque k: 2000+k (como noche.sh).
#
# Reanudable: se salta los bloques cuya AODSIM ya existe y los que están corriendo; si se corta (reinicio,
# Docker cerrado), basta con volver a lanzarlo. Un bloque fallido se reintenta (máx. MAXATT intentos en total,
# contados en state/attempts_causal_bNNN). Contenedores: lw3c-causal-bNNN (sólo toca los suyos).
# Análisis: cuando aparece una AODSIM nueva, corre el analizador v2 (../analysis/run_wdv.sh) en el contenedor
# lw3c-ana (lo crea si no existe) y deja ../analysis/out/sig_causal/lw_zonly_M200_causal_bNNN_AODSIM.root.
# Al terminar NO cierra Docker ni duerme la Mac (hay otros contenedores de la usuaria).

NPAR=${1:-3}; KMIN=${2:-20}; KMAX=${3:-59}
SIG=$(cd "$(dirname "$0")" && pwd); ANA=$(cd "$SIG/../analysis" && pwd)
IMG=cmsopendata/cmssw_5_3_32:latest
CH=$SIG/hepmc_chunks50/causal; MAN=$CH/manifest.txt
MAXATT=4
STATE=$SIG/state; LOGD=$SIG/logs/prod2000; mkdir -p $STATE $LOGD
LOG=$LOGD/prod2000_$(date +%Y%m%d_%H%M).log
log() { echo "$(date '+%F %T')  $*" | tee -a "$LOG"; }

if [ -z "$DRY" ] && [ -z "$LW_CAFFEINATED" ]; then   # no dormir mientras el script vive
  export LW_CAFFEINATED=1
  exec caffeinate -i -s "$0" "$@"
fi
log "inicio. NPAR=$NPAR bloques b$(printf %03d $KMIN)..b$(printf %03d $KMAX) DRY=${DRY:-0}"

if [ -z "$DRY" ]; then
  if ! docker info >/dev/null 2>&1; then
    log "abriendo Docker…"; open -a Docker
    for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 10; done
    docker info >/dev/null 2>&1 || { log "ERROR: Docker no arrancó en 10 min."; exit 1; }
  fi
  for c in $(docker ps -a --filter status=exited --filter status=created --format '{{.Names}}' | grep -E '^lw3c-causal-b[0-9]{3}$'); do
    docker rm "$c" >/dev/null
  done
fi

tagof()  { printf 'b%03d' $1; }
aod()    { echo "$SIG/aod/causal/lw_zonly_M200_causal_$1_AODSIM.root"; }
first()  { awk -v k=$1 '$1==k{print $2}' $MAN; }
running(){ [ -n "$DRY" ] && { echo 0; return; }; docker ps --format '{{.Names}}' | grep -cE '^lw3c-causal-b[0-9]{3}$'; }
is_running() { [ -z "$DRY" ] && docker ps --format '{{.Names}}' | grep -qx "lw3c-causal-$1"; }

pending_list() {
  for k in $(seq $KMIN $KMAX); do
    [ -f "$CH/$(printf 'chunk_%03d' $k).hepmc" ] || continue    # chunk aún no preparado
    [ -f "$(aod $(tagof $k))" ] && continue
    echo $k
  done
}

launch() {
  local k=$1 tag; tag=$(tagof $k); local f; f=$(first $k)
  [ -z "$f" ] && { log "ERROR: $tag no está en el manifiesto"; return 1; }
  local af=$STATE/attempts_causal_$tag; local n; n=$(cat $af 2>/dev/null || echo 0)
  [ "$n" -ge $MAXATT ] && return 1
  if [ -n "$DRY" ]; then log "[DRY] lanzaría causal $tag FIRST=$f SEED=$((2000+k)) (intento $((n+1)))"; return 0; fi
  echo $((n+1)) > $af
  docker rm "lw3c-causal-$tag" >/dev/null 2>&1
  docker run -d --memory 2g --platform linux/amd64 --name "lw3c-causal-$tag" -v "$SIG":/work -e LW_PU=1 $IMG \
    /work/cmssw/run_chunk.sh causal /work/hepmc_chunks50/causal/$(printf 'chunk_%03d' $k).hepmc $f $((2000+k)) $tag 0 -1 >/dev/null \
    && log "lanzado causal $tag FIRST=$f SEED=$((2000+k)) (intento $((n+1)))" || { log "ERROR al lanzar $tag"; return 1; }
}

ensure_ana() {
  docker ps --format '{{.Names}}' | grep -qx lw3c-ana && return 0
  docker rm lw3c-ana >/dev/null 2>&1
  docker run -d --platform linux/amd64 --memory 2g --name lw3c-ana -v "$ANA":/work -v "$SIG/aod":/sigaod:ro $IMG sleep infinity >/dev/null
}

analyze_new() {   # analizador v2 sobre AODSIM nuevas sin salida (secuencial, ~30 s por bloque)
  [ -n "$DRY" ] && return
  for k in $(seq $KMIN $KMAX); do
    local tag b out; tag=$(tagof $k); b=lw_zonly_M200_causal_${tag}_AODSIM
    [ -f "$(aod $tag)" ] || continue
    out=$ANA/out/sig_causal/$b.root; [ -f "$out" ] && continue
    [ "$(cat $STATE/ana_attempts_$tag 2>/dev/null || echo 0)" -ge 3 ] && continue
    ensure_ana || { log "ERROR: no arranca lw3c-ana"; return; }
    echo $(( $(cat $STATE/ana_attempts_$tag 2>/dev/null || echo 0) + 1 )) > $STATE/ana_attempts_$tag
    mkdir -p $ANA/lists/sig_causal $ANA/logs/prod/sig_causal
    echo "file:/sigaod/causal/$b.root" > $ANA/lists/sig_causal/$b.txt
    docker exec lw3c-ana bash /work/run_wdv.sh 0 /work/lists/sig_causal/$b.txt /work/out/sig_causal/$b.tmp.root -1 \
      > $ANA/logs/prod/sig_causal/$b.log 2>&1
    if grep -q 'TrigReport Events total' $ANA/logs/prod/sig_causal/$b.log; then
      mv $ANA/out/sig_causal/$b.tmp.root $out; echo $b >> $ANA/done/sig_causal.txt
      log "analizado (v2) $tag: $(grep 'TrigReport Events total' $ANA/logs/prod/sig_causal/$b.log)"
    else
      rm -f $ANA/out/sig_causal/$b.tmp.root; log "ERROR análisis $tag (ver logs/prod/sig_causal/$b.log)"
    fi
  done
}

ndone() { n=0; for k in $(seq $KMIN $KMAX); do [ -f "$(aod $(tagof $k))" ] && n=$((n+1)); done; echo $n; }
NTOT=$((KMAX-KMIN+1)); log "bloques ya terminados: $(ndone)/$NTOT"

while :; do
  [ -f $STATE/NPAR_2000 ] && NPAR=$(cat $STATE/NPAR_2000)
  r=$(running); launched=0
  for k in $(pending_list); do
    [ "$r" -ge "$NPAR" ] && break
    is_running $(tagof $k) && continue
    launch $k && { r=$((r+1)); launched=1; [ -z "$DRY" ] && sleep 30; }
  done
  [ -n "$DRY" ] && break
  analyze_new
  r=$(running)
  [ "$r" -eq 0 ] && [ "$launched" -eq 0 ] && break
  sleep 120
done

failed=$(for k in $(pending_list); do echo -n "$(tagof $k) "; done)
log "RESUMEN: $(ndone)/$NTOT bloques con AODSIM."
[ -n "$failed" ] && [ -z "$DRY" ] && log "ATENCIÓN: bloques sin AODSIM tras $MAXATT intentos (ver logs/cmssw/causal): $failed"
grep -h DONE $SIG/logs/cmssw/causal/b0[2-5][0-9]_timing.txt 2>/dev/null >> "$LOG"; exit 0
