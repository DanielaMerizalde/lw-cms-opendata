# Phase 3B — progress log (analysis on CMS open data)

- 2026-10-18 ~18:00  Docker up; image cmsopendata/cmssw_5_3_32:latest pulled (14.8 GB).
- Records: data 6005 (/DoublePhoton/Run2012B-22Jan2013-v1/AOD, 1612 files, 24.67 M ev),
  6031 (/DoublePhoton/Run2012C-22Jan2013-v2/AOD, 2719 files, 41.56 M ev); DY 7730; TTbar 9518; W1/2/3 9863/9864/9865.
- Conditions: container-local CondDB extract /opt/cms-opendata-conddb (sqlite), GT FT53_V21A_AN6_FULL::All (data), START53_V27::All (MC).
- HLT path (from record 6005 trigger list): HLT_Photon36_R9Id85_OR_CaloId10_Iso50_Photon22_R9Id85_OR_CaloId10_Iso50_v*
  (the "CaloId22" in the task text does not exist; it is CaloId10).
- WDVAnalyzer compiled OK in container lw3b-main (CMSSW area at phase3/analysis/cmssw).
- 100-event test on one data file: OK, 9/100 pass TF. Real time 0.38 s/ev (CPU 8 ms/ev) -> network bound.
- Geometry from the stripped GT is missing (IdealGeometryRecord) -> TransientTracks now built with the
  magnetic field only (reco::TransientTrack(track, B)); results identical to the GeometryIdeal (XML) version on 2000 events.
- I/O: input slimmed with inputCommands (only needed products). Throughput is network bound,
  ~3.5-4 ev/s per cmsRun job (TCP-window limited, ~0.2 MB/s/stream); scales with parallel jobs
  (5 jobs -> ~17 ev/s aggregate). CPU ~ms/ev except SV fits.
- BLOCKER (partial): all 2012 MC AODSIM records used (7730, 9518, 9863-9865) are "partial":
  ONE file online per record, the rest on tape ("on demand", needs a staging request via the portal).
  -> MC limited to 1 file per background (~1e4 events each). Data fully online.
- Rates per DoublePhoton event (first tests): TF ~6%, OS ~0.3%, SG ~0.1%, SV ~0.07%, WDVC ~0.03%.
- 18:55 production launched: plan.json = 43 random whole data files (16 of 6005 + 27 of 6031, ~1%)
  + 5 online MC files; 12 parallel jobs. Expected ~70 min per file per job -> ETA ~4-5 h.
- 19:05 MC done (1 online file each): W1 8359 ev, W2 12082, TT 5992 (sum of gen-weight signs 3590), W3 7657, DY ~12.6k.
  MC rates: ~20 ev/s per job. Data in production: 10-13 min per 15k-event file (~20-25 ev/s per job,
  much faster than the first tests), ~70 ev/s aggregate with 9 jobs. 1% sample ETA ~20:10.
- 19:15-21:15 throughput dropped: some data files take 1-2 h (slow EOS disk servers), aggregate ~50 ev/s.
  21:15: 31/48 files done (26 data), 0 failures.
- 21:05 Signal test10 AODSIM (phase 3A, 10 ev causal + 10 acausal) analysed in container lw3b-sig
  (phase3/signal/aod mounted read-only at /sigaod): causal TF/OS/SG/SV/WDVC = 5/3/1/0/0,
  acausal 6/3/1/1/1 (9 SV', all kappa<0, L_T 0.02-0.07 mm) -> chain works on the signal, HLT path present.
- Interim (26 data files, 62 pb^-1): data OS-chain cutflow 341606/18709/1050/259/125/55 events;
  SS 467/47/24/7 after OS. DY (1 file, weight ~19/event) 46 raw events at OS -> 871 weighted.

## 2026-10-20 — v2 (tesis USFQ 2022)
- 10-18 21:30: detenido por el usuario con 29/43 archivos de datos + 5 MC hechos con el analizador v1 (ahora obsoleto).
- 10-20 ~18:20: Docker reiniciado; WDVAnalyzer reescrito según el Cap. II de la tesis (trigger OR de 4 caminos,
  cutflow NF/TF/TO/HQ/JetS/DRC/SG/IPP, Tabla 2.1, κ∥ transversal con P_T de trazas, IPP, flip por verdad).
  Compilado OK. Siguiente: señal (21 bloques) + 5 MC, luego reprocesar datos (43 archivos).
- 18:32 producción v2: señal 21/21 bloques OK; MC+datos relanzados con 14 jobs (red ~4 ev/s por job hoy).
- 19:15 red lenta hoy: ~0.7–0.8 MB/s agregados hacia eospublic (14 streams; general 5 MB/s), ~1.5–2 ev/s por job,
  algunos stalls de xrootd ("Failed to read header") que se recuperan. W1, W3 OK (v2). Prueba A/B: cacheSize=0 es peor.
  Señal v2: causal 275 ev -> NF/TF/TO/HQ/JetS/DRC/SG/IPP = 275/185/159/157/98/35/34/21 (IPP sin flip), acausal 250/168/152/145/79/28/28/16.
- 20:12 datos v2:       11 archivos completos; DY en curso.
- 20:42 datos v2:       19/43 archivos
- 21:32 datos v2:       34/43 archivos
- 10-21 ~01:30 v2 COMPLETO: 43/43 datos (610 987 ev, L ≈ 112.8 pb⁻¹ = 0.98 %), 5 MC (1 archivo c/u), señal 11+10 bloques.
  Entregables: plots/cutflow_v2.md, plots/kappa_fig2p5_k_r150|r20.{png,pdf}, plots/signal_flip_vs_reflect_k_r150|r20.{png,pdf},
  plots/signal_investigation.json, plots/ipp_variants.json, plots/ipp_units.json, RESULTS.md. Contenedores lw3b-* detenidos.
- 10-26: estudio de mejoras (solo señal) en mejoras/: V1 (asignación χ² m_jj, m_ejj) + AVF da f(κ<0) 0.31 causal vs 0.72 acausal (7.6σ); limpieza de trazas empeora. Ver mejoras/README.md.
- 10-26 19:29 v3 final: producción lanzada (mejoras/prod_v3.py, plan_final.json: 43 datos + 5 MC + 40 señal, 14 jobs). Salidas en mejoras/out_data/. ETA datos ~2–3 h (red).
- 10-26 19:43 v3 final: señal 40/40 OK (causal 144 SV, f(κ<0)=0.31; acausal 151 SV, f=0.72). MC y datos en curso.
- 10-26 20:30 v3 final datos:       10/43 archivos
- 10-26 21:00 v3 final datos:       18/43 archivos
- 10-26 21:30 v3 final datos:       26/43 archivos
- 10-27 17:10 v3 final reanudado (27/43 datos hechos; Docker reiniciado tras interrupción).
- 10-27 19:06 v3 final COMPLETO: 43/43 datos, gráficas en mejoras/plots_final/.
- 10-28 diagnóstico problema 1 (velocidad): edmEventSize → generalTracks 58 kB/ev, particleFlow 39 kB/ev de ~263 kB/ev; prueba ROOT 3000 ev: sólo ramas pequeñas (trigger, e, jets, PV) 10.9 kB/ev y 30 ev/s/conexión vs 115.5 kB/ev y 7.1 ev/s con trazas+PF. Propuesta: análisis en dos pasadas (~10× menos datos). xrdcp 1 conexión ≈ 4.7 MB/s. Presentación: https://claude.ai/artifact/7wPsHpKtNEJWkq3G639eR2
- 11-10 ~20:00 QCD desde datos lanzado: `qcd/prod_qcd.py --njobs 6` (48 archivos: 43 datos + 5 MC), contenedor lwqcd con límite subido de 2 a 6 GB (`docker update`), caffeinate atado al proceso. Registro: qcd/prod_qcd.log. ETA ~5–7 h (red). Reanudable con el mismo comando (ver qcd/README.md). **Detenido a petición de la usuaria (~20:20) antes de terminar ningún archivo; salidas parciales .tmp borradas, límite de lwqcd devuelto a 2 GB.**
