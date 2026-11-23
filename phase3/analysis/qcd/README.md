# QCD desde datos (2026-11-09)

**Objetivo:** estimar el fondo QCD multijet (electrones falsos) **a partir de los datos**, porque el MC está
en cinta y no se puede recuperar. Solo trata QCD. DY y tt̄ (electrones reales) siguen pendientes.

## Qué se cambió
- **`src/LWQCD/WDVQCD/plugins/WDVQCDAnalyzer.cc`**: es una copia de **WDVAnalyzer v2**. La selección, los
  vértices y κ∥ son idénticos; se comprobó con el bloque de señal b000: el cutflow y los vértices con su κ∥
  salen iguales. **No corta por ID ni por aislamiento**; solo guarda información nueva:
  - por electrón: `e_iso` (aislamiento PF relativo, corregido por pileup con ρ·A_eff) y `e_idBits`;
  - los bits 1/2/4 son loose/medium/tight **con** aislamiento (= POET);
  - los bits 8/16/32 son loose/medium/tight **sin** el corte de aislamiento;
  - también las variables crudas del ID (σiηiη, H/E, Δη, Δφ, dxy, dz, 1/E−1/p, hits perdidos, veto de
    conversión);
  - árbol nuevo **`elA` (nivel A):** todos los eventos con trigger y dos electrones (TO + HQ), **sin exigir
    jets**. Guarda m_ee, el número de jets y las mismas variables de electrones. Sirve para medir R y el
    factor tight-to-loose con muchos más eventos.
- El ID es el de POET (rama 2012, `ElectronAnalyzer.cc`), con **una corrección**: POET calcula los
  *missing hits* como `expectedInner − todos los hits válidos`, que siempre da negativo. Así, su corte de
  hits perdidos nunca actúa. Aquí se usa la definición estándar de EGamma: `trackerExpectedHitsInner().numberOfHits()`.
- **Área CMSSW separada** (`qcd/cmssw/`) y **contenedor separado** (`lwqcd`). El área de v2 que usa la
  producción de señal (`/work/cmssw`, contenedor `lw3c-ana`) **no se tocó**.

## Método (`qcd_desde_datos.py`)
1. **R = OS/SS** medido en la región **anti-aislada** (ambos electrones con iso ≥ 0.15), restando el MC
   disponible. Se mide a nivel A (todos, con ≥1, ≥2 y ≥4 jets) y al nivel del análisis, para ver si R
   depende de los jets.
2. **QCD en OS = R × (datos SS − MC SS).** La forma de κ∥ de QCD se toma de los vértices de los eventos SS.
3. **f(κ∥<0)** con errores calculados por **eventos** (bootstrap), no por vértices.
4. **Comprobación tight-to-loose:** F = tight / (loose-sin-iso y no tight) en electrones SS de nivel A fuera
   del Z, separado en barril y endcap. Se aplica a la región OS con ambos electrones tight.

## Cómo ejecutarlo (mañana)
```bash
cd ~/Downloads/lee-wick/lw-cms-opendata/phase3/analysis/qcd
docker start lwqcd                        # ya está creado y compilado
nohup python3 prod_qcd.py --njobs 2 > prod_qcd.log 2>&1 &
tail -f prod_qcd.log
```
- Por defecto procesa los mismos archivos que v2: los 43 de datos (~113 pb⁻¹) y 1 de cada MC.
  Es reanudable: si se corta, se vuelve a lanzar el mismo comando.
- **Memoria:** mientras la producción de señal siga en marcha (3 contenedores de ~1.6 GB, Docker con
  7.7 GB), usar `--njobs 1` o `2`. Cuando termine, se puede subir a 4–6.
- Al final:
```bash
cd ~/Downloads/lee-wick/lw-cms-opendata/phase3/analysis
.venv/bin/python qcd/qcd_desde_datos.py
```
  Los resultados quedan en `qcd/plots/`: `qcd_resumen.md`, `qcd_numeros.json`, `kappa_qcd.png` y
  `mee_regiones.png`.

## Pruebas hechas (2026-11-09)
- Señal b000 (25 eventos): el cutflow OS/SS y los vértices con su κ∥ son **idénticos** a la salida v2.
- Datos, 3000 eventos de un archivo de 2012B por XRootD: corre sin errores, en 96 s.
  - El árbol `elA` tiene 213 eventos; 156 de los 187 OS caen en 80 < m_ee < 100 (pico del Z).
  - El 26 % de los electrones tiene iso > 0.15, así que la región anti-aislada existe.
  - El veto de conversión y ρ se leen bien.

## Advertencias
- Los triggers de la tesis llevan aislamiento a nivel HLT (`CaloId10_Iso50`), salvo las rutas `R9Id85`.
  La región anti-aislada puede quedar sesgada por el trigger. `hltBits` permite comprobarlo separando
  por ruta.
- Restar el MC en las regiones de control usa 1 archivo por muestra (peso DY ≈ 34 por evento). Esa resta
  es ruidosa, pero en las regiones SS y anti-aisladas debería ser pequeña.
- El tight de POET exige |dxy| < 0.2 mm. **No se usa como corte** en la región de señal; solo sirve como
  herramienta para el método 2.

## Corrida con todos los datos (2026-11-12)
- **Archivos:** las listas de los 4331 archivos de datos (11.5 fb⁻¹) están en `lists_full/`, y el MC está copiado ahí.
  Se lanza con `nohup caffeinate -i -s ./lanzar_todos.sh 5 > lanzar_todos.log 2>&1 &` y se vigila con `./vigilar_todos.sh`.
  Es reanudable.
- **Modo rápido `lazyHQ=1`:** hay una sola pasada. La lectura pesada de cada archivo eran las trazas (`generalTracks`,
  53 kB/ev) y las partículas PF (`particleFlow`, 36 kB/ev), y solo se necesitan para el corte HQ y los vértices. Ahora el
  corte HQ se evalúa recién en el paso de vértices, así que lo pesado se lee solo para las ~9 colisiones por archivo
  que llegan ahí.
  - Medido sobre un archivo completo: 203 s y ~21 kB/ev, frente a ~100 kB/ev antes. El árbol `events` (κ∥) sale
    **idéntico**.
  - Cambio: el árbol `elA` (nivel A) queda **sin el corte HQ** (rama `hq = -1`) y tiene ~14 % más eventos. R a nivel A y
    el método 2 se miden sin HQ.
- La salida del 1 % (43 archivos) quedó en `out_1pct/`, `done_1pct/`, `plots_1pct/` y `lanzar_todo_1pct.log`.
- La luminosidad se calcula con `lumi_qcd.py` (fracción de bytes por dataset) → `lumi_qcd.json`, que `qcd_desde_datos.py` lee.
- Contenedor `lwqcd`: el límite de memoria se subió a 6 GB (`docker update`) para correr 5 trabajos.
