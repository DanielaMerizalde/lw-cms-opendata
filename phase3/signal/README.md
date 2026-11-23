# Fase 3A: señal sólo-Z (M = 200 GeV) con simulación y reconstrucción completas de CMS 2012 (CMSSW_5_3_32)

Escenario de normalización del **paper** (Sánchez, ACI 15(1) 2780): señal **sin intercambio de fotón**,
`p p > z > elw+ elw-`, que reproduce la Tabla 1 (5.95 fb a M = 200 GeV). Versiones **causal** y **acausal**
(SV′ = 2PV − SV) de **los mismos eventos**, pasadas por GEN-SIM → DIGI/L1/HLT (con pile-up 2012) → RECO → AODSIM.
Estado y tiempos en vivo: `PROGRESS.md`.

## 1. Generador (paso 1)

| | |
|---|---|
| MG5_aMC 3.8.1 | UFO restringido de la fase 2 (copia en `mg5/ufo/`), `param_card_M200.dat` de la fase 2 (etaLW = +1, lwRep = 0, MeLW = 5·10⁻⁴, WLW = 7.28775·10⁻¹²), nn23lo1, sin cortes, `time_of_flight = 0` |
| proceso | `generate p p > z > elw+ elw-, (elw+ > e+ z, z > qz qz), (elw- > e- z, z > qz qz)`, qz = u c d s b + anti (`mg5/proc_zonly_chain.mg5`) |
| σ inclusiva sólo-Z | **5.955 ± 0.008 fb** (`PROC_lw_zonly_incl`, 10k ev; paper 5.97 fb, fase 2 5.950 fb) |
| σ cadena (×BR(Z→had)² LO de MG5) | 2.406 ± 0.014 fb (cociente 0.404, igual que γ+Z en la fase 2: 17.22/42.30 = 0.407) |
| eventos | 2000, semilla MG5 3201, Pythia 3200 |
| Pythia 8.317 | mismo driver y tarjeta de la fase 2 (`generation/events/pythia/lw_pythia_hepmc`, `lw_8TeV_CUETP8M1.cmnd`), llamados sin modificar |
| reflexión | `generation/events/tools/lw_reflect_hepmc.py` (sin modificar) |
| chequeo HepMC | `hepmc_vertex_check.py`: **RESULT PASS** — 4000 ẽ, 0 descendientes en el PV, `refl_ok` = 4000, líneas P idénticas, κ > 0 en 100 % causal y < 0 en 100 % acausal (`gen/samples/vertexcheck_zonly_M200.log`) |

Scripts: `mg5/run_mg5_zonly.sh`, `gen/run_gen_zonly.sh`. Salida: `gen/samples/` (LHE, HepMC causal/acausal .gz, CSV de verdad).

### Comparación sólo-Z frente a γ+Z (cierra el punto abierto de la fase 2)
`gen/compare_zonly_vs_gz.py`, `gen/costheta_star.py` → `gen/plots/`. 2000 ev sólo-Z frente a los 20 000 γ+Z de la fase 2, verdad:

| variable | sólo-Z | γ+Z | KS D | p |
|---|---|---|---|---|
| ⟨βγ⟩ | 2.16 | 2.05 | 0.042 | 4·10⁻⁶ |
| ⟨βγ_T⟩ | **0.904** | 0.733 | 0.151 | 10⁻⁷² |
| ⟨L⟩ (μm) | 59.6 | 55.6 | 0.034 | 5·10⁻⁴ |
| ⟨L_T⟩ (μm) | **25.7** | 20.0 | 0.071 | 2·10⁻¹⁶ |
| f(L_T > 20 μm) | **38.2 ± 0.8 %** | 31.5 ± 0.2 % | | |
| ⟨p_T(e)⟩ (GeV) | 91.9 | 82.9 | 0.075 | 2·10⁻¹⁸ |
| η(e) | | | 0.026 | 0.01 |
| ⟨p_T(jet)⟩ (GeV) | 77.5 | 70.0 | 0.046 | 10⁻¹⁴ |
| N_jets (p_T > 20) | 4.36 | 4.32 | 0.013 | 0.91 |
| ⟨m(ẽẽ)⟩ (GeV) | **642** | 567 | 0.216 | 4·10⁻⁷⁵ |
| ⟨cos²θ*⟩ | 0.401 | 0.362 | 0.047 | 7·10⁻⁴ |

**Las distribuciones NO son iguales.** La diferencia principal es que el espectro de m(ẽẽ) es más duro en sólo-Z
(el umbral está más suprimido: la parte axial del acoplamiento Z–ẽ entra como β³ y el fotón, puramente vectorial, como β).
Más masa invariante → mayor p_T del ẽ → βγ_T un 23 % mayor y más ẽ con L_T > 20 μm (38 % frente a 31.5 %).
La distribución angular apenas cambia. Por tanto la elección de normalización también cambia la **forma** de la señal
y no sólo σ: para reproducir el paper hay que usar esta muestra sólo-Z, no reescalar la γ+Z.

## 2. Simulación y reconstrucción CMS 2012 (paso 2)

### Contenedor y entorno
- Imagen **`cmsopendata/cmssw_5_3_32:latest`** (Docker Hub, id 9b69cf761c02; CMSSW_5_3_32, slc6_amd64_gcc472),
  `docker run --platform linux/amd64` sobre Apple silicon (emulación; ≈ 3–5 veces más lento que nativo).
  VM de Docker Desktop: 8 CPU, 7.7 GB de RAM (compartida con el agente de la fase 3B).
- Montaje: `phase3/signal` → `/work`. Contenedores `lw3a-*`.
- Área CMSSW persistente `cmssw/CMSSW_5_3_32` con un único paquete propio (ver abajo); `run_chunk.sh` hace `cmsenv` en ella.

### Receta (registro 12052 de CERN Open Data, ref. [14] del paper)
`EventProductionExamplesTool`, rama 2012, ejemplo `MCQCDProductionMLTrackInfo` (E. Carrera et al.). Los comandos
exactos de `cmsDriver.py` están en `cmssw/driver/make_configs.sh` y las configuraciones generadas en `cmssw/driver/raw_*.py`:

1. **GEN-SIM**: `--step GEN,SIM --beamspot Realistic8TeVCollision --conditions START53_V27::All --eventcontent RAWSIM
   --customise SimWithCastor_cff.customise` (la receta usa *Realistic8TeVCollision*: X0 = 0.244 mm, Y0 = 0.393 mm,
   Z0 = 0.41 mm, σ_z = 6.16 cm, β* = 70 cm).
2. **DIGI,L1,DIGI2RAW,HLT:7E33v2** con `--pileup 2012_Summer_50ns_PoissonOOTPU`, `--runsScenarioForMC Run2012_AB_C_D_oneRunPerEra`
   y el archivo MinBias de la receta
   `root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2012/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM/START50_V13-v3/0002/FEF2F4CC-0E6A-E111-96F6-0030487F1C57.root`
   (19 860 eventos, leído por xrootd en streaming desde el contenedor).
3. **RAW2DIGI,L1Reco,RECO** → **AODSIM** (la receta añade VALIDATION/DQM, que no hacen falta y se quitaron).

Configuraciones finales (envoltorios sobre los `raw_*.py`): `cmssw/cfg/{gensim,hlt,reco}_cfg.py` + `common.py`. Cambios:
- **Fuente HepMC**: `MCFileSource` (IOMC/Input) lee el HepMC2 de Pythia (`U GEV MM`, sin descomprimir: los chunks
  son ASCII plano). El generador Pythia6 de relleno del cmsDriver se elimina. Problema encontrado: `MCFileSource` hereda
  de `ExternalInputSource` con `realData = true`, así que **marca los eventos como datos reales** y el paso HLT aborta
  (`setRunNumber ... cannot be used with real data`); además el AODSIM habría quedado con `isRealData() = true`.
  Solución: plugin **`LWMCFileSource`** (`cmssw/build_plugin.sh`): copia literal de MCFileSource + HepMCFileReader
  con la única diferencia `ExternalInputSource(pset, desc, false)`.
- **Recableado de la etiqueta**: el HepMCProduct se llama `source`, no `generator`:
  `VtxSmeared.src`, `genParticles.src` y `g4SimHits.Generator.HepMCProductLabel` = `source`. En 5_3_X el
  `BetafuncEvtVtxGenerator` desplaza el evento HepMC **en el sitio** (`applyVtxGen`), así que genParticles y Geant4
  ven los vértices ya con el beamspot (desplazamiento rígido de todo el evento).
- `keep edmHepMCProduct_source_*_*` en todas las salidas; en AODSIM además `SimTracks`/`SimVertexs` de `g4SimHits`
  (no estándar; ~10 % del tamaño) para estudios de verdad de vértices.
- **Números aleatorios comunes**: semilla maestra = 1000 + chunk, la misma para causal y acausal.
  `RandomNumberServiceHelper.populate()` y `ThrowAndSetRandomRun` usan `random.SystemRandom` (no reproducible), lo que
  daba beamspot, run (194533/200519/206859) y PU distintos entre las dos versiones (visto en el primer test).
  Se sustituyeron por sorteos con `random.Random(semilla)`. Comprobado: semillas y run idénticos en ejecuciones repetidas.
  Geant4 diverge igualmente en cuanto difieren los primeros pasos (las partículas del ẽ empiezan en otro sitio).
- `EventID.event` = índice HepMC + 1 (`firstEvent`), para emparejar eventos causales y acausales y con los CSV de verdad.

### Condiciones
Global tag **START53_V27::All** (el de la receta) leído por **Frontier** a través de los servidores de
`cms-frontier.openhtc.io:8080` que vienen en el `site-local-config.xml` de la imagen (no hay CVMFS en el contenedor).
La imagen trae un extracto local `/opt/cms-opendata-conddb/START53_V27_MC_stripped.db` + 37 payloads (12 MB), pero
sólo cubre las etiquetas de análisis (JEC, etc.), no las de SIM/DIGI/L1/HLT/RECO, así que no sirve para producir.
Coste: la carga de condiciones sin squid local tarda ~2 min (GEN-SIM), ~13 min (HLT, incluye menú y apertura del PU)
y ~7 min (RECO) por job. Con chunks de 50 eventos eso es ≈ 8 % del tiempo de un job, por lo que no se montó un
squid local (habría que descargar otra imagen, p. ej. frontier-squid; queda como mejora posible).

### Pile-up
Sí: perfil `2012_Summer_50ns_PoissonOOTPU` (el de Summer12_DR53X), con el **único** archivo MinBias de la receta.
Limitación: 19 860 eventos MinBias para ~4000 × ~20 × (BX −2…+3) extracciones → los eventos de PU se reutilizan muchas veces
(como en la receta). Las versiones causal y acausal de un chunk usan el mismo run y las mismas semillas de mezcla.

### Paralelización
Los HepMC se trocean en 40 chunks de 50 eventos (`gen/split_hepmc.py` → `hepmc_chunks/{causal,acausal}/`).
`cmssw/launch_production.sh` lanza un contenedor por chunk y versión (`lw3a-<versión>-cNNN`, `--memory 2g`), con
NPAR trabajos a la vez (fichero `cmssw/NPAR`, editable en caliente); salta los chunks ya hechos. Cada contenedor
ejecuta `cmssw/run_chunk.sh` (GEN-SIM → HLT → RECO; borra los intermedios si todo va bien).
Salida: `aod/{causal,acausal}/lw_zonly_M200_<versión>_cNNN_AODSIM.root`; logs en `logs/cmssw/<versión>/`.

### Verificación
`cmssw/verify/verify_edm.py` (FWLite, python 2.6 del contenedor) + `cmssw/verify/summarize_verify.py` (host).
(RESULTADOS: ver §3)

## 3. Resultados de la verificación
(se completa abajo)
