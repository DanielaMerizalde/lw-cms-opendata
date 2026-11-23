# Fase 3B — Análisis en datos abiertos de CMS (2012, 8 TeV)

Reproducción desde cero del análisis de J. Sánchez, ACI 15(1) 2780 (2023): selección, reconstrucción
de vértices secundarios (SV), paralelidad κ∥ y la Fig. 2. El análisis corre con CMSSW_5_3_32 sobre AOD,
leídos por xrootd desde `eospublic.cern.ch`. No se descargó ningún AOD.

El estado, los rendimientos y la cronología están en `PROGRESS.md`. Los resultados numéricos están en
`plots/` (`cutflow_*.md`, `kappa_fig2_*.json/png/pdf`).

## Estructura

| Ruta | Contenido |
|---|---|
| `src/LWAnalysis/WDVAnalyzer/plugins/WDVAnalyzer.cc` | EDAnalyzer: TF, OS, SG, SVRA, κ∥, WDVC, ntuple plano y cutflow |
| `src/LWAnalysis/WDVAnalyzer/python/wdv_cfg.py` | configuración de cmsRun (todos los cortes son parámetros) |
| `setup_build.sh`, `run_wdv.sh` | compilación y ejecución dentro del contenedor (`lw3b-main`) |
| `make_plan.py`, `plan.json` | elección de archivos (semilla fija) |
| `prod.py` | orquestador (N cmsRun en paralelo, reanudable: `done/<muestra>.txt`) |
| `lumi_calc.py`, `lumi_processed.json` | luminosidad de la fracción procesada |
| `plot_kappa.py` | Fig. 2 (pila κ∥, cociente, banda sistemática) y tablas de cutflow |
| `plot_signal.py` | señal: causal con signo invertido frente a acausal reflejada |
| `filelists/`, `meta/` | listas xrootd con tamaños y metadatos de los registros |
| `out/<muestra>/*.root` | ntuples (un archivo por AOD de entrada) |
| `logs/` | logs de cmsRun |

## Entorno y condiciones

- Imagen `cmsopendata/cmssw_5_3_32:latest`, `--platform linux/amd64`, emulada en Apple silicon.
  Contenedores `lw3b-main` (datos y fondo) y `lw3b-sig` (señal, con `phase3/signal/aod` montado solo lectura).
- **Condiciones:** la imagen trae un extracto local de la CondDB en `/opt/cms-opendata-conddb/`, en sqlite.
  - Datos: `connect = sqlite_file:/opt/cms-opendata-conddb/FT53_V21A_AN6_FULL_data_stripped.db`, GT `FT53_V21A_AN6_FULL::All`. Contiene JEC Summer13_V4, incluido el residual.
  - MC: `START53_V27_MC_stripped.db`, GT `START53_V27::All`.
  - No hace falta CVMFS ni Frontier. El nombre `FT53_V21A_AN6::All` no existe en el extracto; hay que usar el sufijo `_FULL`.
- El extracto no incluye la geometría (`IdealGeometryRecord`), así que `TransientTrackBuilder` falla. Las
  `reco::TransientTrack` se construyen directamente con el campo magnético
  (`TransientTrack(track, B)`, campo de `MagneticField_38T_cff`). KVF e IPTools solo necesitan el campo.
  Se comprobó que da resultados idénticos a la versión con geometría XML ideal, en 2000 eventos.
- JSON certificado: `data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt` (registro 1002 del portal),
  aplicado con `lumisToProcess`.
- La entrada se adelgaza con `inputCommands`, conservando solo los productos usados. Así el rendimiento por la
  red mejora mucho.

## Muestras

| Muestra | Registro | Dataset | σ usada |
|---|---|---|---|
| Datos B | 6005 (CEPG.EXLP) | /DoublePhoton/Run2012B-22Jan2013-v1/AOD | L = 4.412 fb⁻¹ |
| Datos C | 6031 (KT69.ANB8) | /DoublePhoton/Run2012C-22Jan2013-v2/AOD | L = 7.055 fb⁻¹ |
| Z→ℓℓ | 7730 | DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball, PU_RD1_START53_V7N | 3503.7 pb (paper) |
| tt̄ | 9518 | TTbar_8TeV-Madspin_aMCatNLO-herwig, PU_S10_START53_V19 | 225.2 pb (paper) |
| W+1j | 9863 | W1JetsToLNu_TuneZ2Star_8TeV-madgraph | 6662.8 pb |
| W+2j | 9864 | W2JetsToLNu_TuneZ2Star_8TeV-madgraph | 2159.2 pb |
| W+3j | 9865 | W3JetsToLNu_TuneZ2Star_8TeV-madgraph | 640.4 pb |

- **σ de W+jets:** el paper da 1.75×10⁻¹ pb, que es casi seguro una errata. Los registros del portal no traen
  σ. Se usan los valores LO de MadGraph (5400, 1750, 519 pb) escalados a NNLO con el factor inclusivo
  (≈1.23), que es lo habitual en análisis de CMS a 8 TeV (6662.8 / 2159.2 / 640.4 pb). Son valores tomados de
  la literatura y la twiki de CMS, no se verificaron aquí. La σ de W1+W2+W3 no cambia nada en la práctica,
  porque su contribución tras la selección es nula o casi nula.
- **tt̄ aMC@NLO** tiene pesos negativos. Se usa el signo de `GenEventInfoProduct::weight()`, y la normalización
  es N_gen = Σ signos.
- **Limitación importante:** en los registros MC de 2012 usados, **solo un archivo por registro está
  en disco (online)**. El resto está en cinta ("on demand") y habría que pedir que lo restauren desde el portal.
  Por eso el fondo simulado está limitado a 1 archivo por muestra (≈10⁴ eventos cada uno). Su estadística
  después de OS es prácticamente nula. El fondo dominante, QCD, se estima con datos (región SS), así que la
  Fig. 2 sigue siendo significativa.
- **Sin repesado de pileup ni factores de escala** de eficiencia. El paper no los menciona.

## Selección (paper, pp. 4–6) y decisiones tomadas

**TF:**
- Trigger `HLT_Photon36_R9Id85_OR_CaloId10_Iso50_Photon22_R9Id85_OR_CaloId10_Iso50_v*`. El nombre se verificó
  en la lista de triggers del registro 6005. En el enunciado aparecía "CaloId22", que no existe.
- ≥2 `gsfElectrons` con E_T(SC) > 36 y 22 GeV. Se interpreta "los dos egamma son electrones" como pedir que
  los dos egamma más energéticos sean `gsfElectrons`.
- ≥4 jets ak5PF corregidos con pT > 15 GeV.

**OS:**
- PV bueno (no fake, ndof > 4, |z| < 24 cm, ρ < 2 cm) y filtro de beam-scraping (fracción highPurity > 25 % si hay
  ≥10 trazas), ambos de JHEP 02 (2013) 085.
- Electrones con pT > 40 y 25 GeV y |η_SC| < 2.5, fuera de 1.4442–1.566. Si hay más de dos, se toman los dos
  de mayor pT.
- "Trazas de alta calidad" según JHEP 02 (2013) 085: la traza general asociada (`closestCtfTrackRef`) debe
  existir y ser `highPurity`.
  - No se aplica |d0/σ| > 3 de esa referencia, porque eliminaría la señal: λ ≈ 27 µm, del orden de la
    resolución.
  - La isolación de trazas de cono hueco (0.03 < ΔR < 0.3, Σp_T < 4 GeV) se guarda en el ntuple pero no se
    aplica.
- ≥4 jets ak5PF con JEC del GT (L1FastJet+L2+L3, más L2L3Residual en datos), pT > 20 GeV, ≥2 constituyentes y
  fracción EM < 0.6. La fracción EM se define como chargedEm + neutralEm. Este corte elimina el jet que
  contiene al electrón. No hay limpieza explícita jet–electrón.

**SG:**
- El par de electrones debe tener carga opuesta. La región de control SS es idéntica, salvo que pide la misma
  carga.
- |ΔR1 − ΔR2| < 0.2, con ΔR al jet seleccionado más cercano y al segundo más cercano, para **al menos uno**
  de los dos electrones. El ntuple guarda la bandera por electrón.

**SV (SVRA de arXiv:1610.05133, Sec. 5.1):**
- Para cada electrón seleccionado (los dos) y cada par de jets con **80 < m_jj < 160 GeV**:
  - La traza del electrón es la traza general (`closestCtfTrack`). Si no existe se usa la GSF, aunque nunca
    ocurre porque OS exige la traza general highPurity.
  - Se añaden las trazas de los constituyentes PF de los dos jets con pT > 1 GeV, ≥8 hits válidos y ≥1 hit de
    píxel, quitando duplicados.
  - El corte |d_xy| > 100 µm de 1610.05133 **no se aplica** (parámetro `trkMinDxy` = 0), porque la señal tiene
    λ ≈ 27 µm.
- Se ajustan todos los pares de trazas con `KalmanVertexFitter` y se conservan los de χ²/ndf < 5.
- Fusión iterativa de vértices que comparten trazas, como en 1610.05133:
  - Si la significancia de la distancia 3D es < 4, se reajusta la unión. Si χ²/ndf < 5, la unión reemplaza
    a ambos vértices.
  - Si no, cada traza compartida se asigna por la significancia del parámetro de impacto 3D. Si es < 1.5 en
    ambos, va al vértice con más trazas. Si es > 5 en uno, se quita de ese. En los demás casos va al de menor
    significancia.
  - Se reajusta. El vértice se elimina si falla el ajuste.
- SV' final:
  - Debe contener la traza del electrón, tener ≥5 trazas y χ²/ndf < 5.
  - Requisitos de 1610.05133 Sec. 5.2: ≥3 trazas con pT > 3 GeV; algún par con ΔR < 0.4; algún par con
    ΔR > 1.2; todos los pares con ΔR < 4; d_BV < 25 mm; σ(d_BV) < 25 µm.
  - Todas las banderas se guardan en `sv_flags`. El bit 64 indica que pasa todos los requisitos.
- Si se encuentra el mismo vértice con otro par de jets, se descarta el duplicado.
- PV: el primer `offlinePrimaryVertices` bueno, que es el de mayor Σp_T².

**κ∥ = (SV − PV)·P_tot**, en 3D y en mm·GeV (las longitudes de CMSSW están en cm, ×10):
- `sv_kobj` (por defecto): P_tot = p(e) + p(j1) + p(j2), con los objetos del vértice.
- `sv_ktrk`: P_tot = suma de los momentos de las trazas del SV.
- `sv_kobjT`: versión transversal, solo como diagnóstico.

**WDVC**, por electrón:
- ≥1 SV' asociado a la traza del electrón.
- **Todos** los SV' de ese electrón con |PV→SV'|_T > 0.02 mm.
- |P_tot|_T > 20 GeV (P_tot de los objetos) en al menos un SV'.
- El evento pasa si algún electrón pasa. La Fig. 2 rellena κ∥ de los SV' de los electrones que pasan la WDVC
  (`--stage wdvc`). Con `--stage sv` usa todos los SV' tras el paso SV.

**QCD:**
- La plantilla es data_SS − MC_SS, bin a bin en κ∥ y en la misma etapa de selección. Se extrapola a OS con
  R_OS/SS = 1, como en el paper: se ajusta en SS y se extrapola.

**Señal:**
- σ del paper (sólo-Z, M = 200 GeV): 5.97 fb × BR(Z→had)² = 0.4887.
- N_gen = eventos procesados.
- Se muestran dos versiones:
  - la muestra causal con κ∥ → −κ∥ (método del paper);
  - la muestra acausal reflejada (SV' = 2PV − SV, el WDV "verdadero", producida en la fase 3A).

**Sistemática (Tabla 2):** 18, 3, 1, 3, 2, 3 y 1 %, sumados en cuadratura (18.9 %), más la estadística de
MC/SS.

## Luminosidad procesada

brilcalc no está disponible. Se usa L_d × (bytes de los archivos procesados completos / bytes del dataset), para
cada dataset. Como verificación cruzada se usa la fracción de lumisecciones certificadas vistas (ver
`lumi_calc.py` y `lumi_processed.json`). La selección de archivos es aleatoria con semilla fija
(`make_plan.py`), y siempre se procesan archivos completos.

## Resultados

Ver la sección final de `PROGRESS.md` y `plots/`.

---

## Versión 2 (20-10-2026): alineada con la tesis de maestría (Sánchez, USFQ 2022, Cap. II)

**La v2 reemplaza a la v1.** Las salidas de la v1 están archivadas en `v1/`.

**Cambios en `WDVAnalyzer.cc`** (los nombres y el orden del cutflow siguen la Tabla 2.2 de la tesis):

| Corte | Definición v2 |
|---|---|
| NF | todos los eventos leídos (datos: tras el JSON) |
| TF | OR de los 4 caminos de la tesis (`HLT_Photon36_CaloId10_Iso50_Photon22_CaloId10_Iso50_v*`, `..._Photon22_R9Id85_v*`, `HLT_Photon36_R9Id85_Photon22_CaloId10_Iso50_v*`, `HLT_Photon36_R9Id85_Photon22_R9Id85_v*`) + ≥2 GSF con pT>20 + ≥4 jets corregidos pT>15. El camino combinado `..._OR_...` se guarda solo como bandera (`hltBits`, bit 8); los bits 0–3 indican qué camino de la tesis disparó. |
| TO | los dos objetos egamma de trigger más energéticos (objetos del último filtro con objetos guardados de cada camino disparado, en `hltTriggerSummaryAOD`) deben estar emparejados (ΔR<0.2 al SC) con GSF distintos, con pT>40 y >25 GeV y |η_SC|<2.5. Si `trigMatch=0`, se toman los dos GSF de mayor pT. En la señal de prueba, el emparejamiento conserva 12 de 13 eventos TF. |
| HQ | ambos electrones con traza general `highPurity` (JHEP 02 (2013) 085) |
| JetS | ≥4 jets con pT>20, |η|<2.5, ≥2 constituyentes, NHEF<0.9, NEMEF<0.9, MEF<0.8 y EMEF<0.6. EMEF se define como chargedEm+neutralEm, porque la tesis lista NEMEF por separado. |
| DRC | |ΔR1−ΔR2|<0.2 para al menos un electrón |
| SG | carga opuesta. El canal SS (misma carga de los dos objetos TO) es la región de control de QCD. |
| IPP | algún electrón con un SV de κ∥<0 y |P_T|>20 GeV, y con todos los demás SV de ese electrón con L_T>0.02 mm |

**SVRA:**
- Trazas con pT>1 GeV, sin cortes de hits, tal como la tesis. Se usan la traza del electrón y las de los constituyentes de un par de jets con 80<m_jj<160 GeV.
- Todos los pares de trazas se ajustan con KVF y se conservan los de χ²/ndf<5.
- Dos vértices que comparten trazas se reajustan juntos. La fusión se acepta si χ²/ndf<5 y si son "geométricamente compatibles". Esto último se define como significancia de la distancia 3D < 4, como en 1610.05133. Si la fusión no se acepta, se conservan ambos vértices y ese par no se reintenta.
- Se itera hasta que no quedan pares que compartan trazas sin haberse intentado.
- Tabla 2.1: ≥5 trazas; ≥3 trazas con E>3 GeV (se usa |p|); algún par con ΔR<0.4; algún par con ΔR>1.2; todos los pares con ΔR<4.
- Solo se guardan los SV que contienen la traza del electrón.

**κ∥ transversal (tesis):**
- Definición por defecto: `sv_k` = (PV→SV)_T · P_T en mm·GeV, con P_T = Σ p_T de las trazas del SV.
- Variantes en el ntuple: `sv_kobjT` (P_T de e+j+j), `sv_k3trk` y `sv_k3obj` (3D).
- El histograma de la Fig. 2.5 se llena en la etapa SG con los SV que tienen L_T>0.02 mm.

**Señal:**
- El electrón de señal se identifica por verdad: el padre del electrón generado tiene |pdg|=9000011 y ΔR<0.1 con la misma carga.
- Muestra causal: para los SV de ese electrón se invierte el signo de κ∥ (`passIPPflip` aplica el flip en el IPP).
- Muestra acausal reflejada: sin flip.

**Normalización:**
- Datos: escalado a la luminosidad completa con la fracción de bytes procesados (`lumi_calc.py`). NF completo = 66 235 981 eventos.
- MC: σ·L/N_gen.
- Señal: 5.97 fb × L, con ×BR(Z→had)² = 0.4887 (nuestra convención) y sin BR (convención de la tesis, donde NF = 67.7 = 5.97 fb × ~11.3 fb⁻¹ con Z forzado a quarks).
- En la Tabla 2.2 de la tesis, NF del MC es σ×L. Para WJets eso implica σ_W ≈ 8434 pb. El 1.75×10⁻¹ pb del texto es, por tanto, una errata.

**QCD:** en la región SS de la etapa SG e IPP se calcula (datos − MC). Esa diferencia se extrapola a OS con R=1, tanto bin a bin en κ∥ como en los conteos.

**Producción:** `plan_v2.json` (señal → MC → datos), con hasta 14 trabajos en paralelo. Los gráficos y tablas se generan con `plot_v2.py`; los resultados están en `RESULTS.md`.
