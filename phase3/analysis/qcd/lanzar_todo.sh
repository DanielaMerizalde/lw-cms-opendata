#!/bin/bash
# Corre WDVQCDAnalyzer sobre los 48 archivos y, al terminar, qcd_desde_datos.py. Mantiene la Mac despierta.
cd "$(dirname "$0")"
echo "inicio: $(date)"
python3 prod_qcd.py --njobs 4
docker stop lwqcd >/dev/null
cd .. && .venv/bin/python qcd/qcd_desde_datos.py
echo "fin: $(date)"
