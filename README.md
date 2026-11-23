# Electrones de Lee-Wick con CMS Open Data 2012 (pp a 8 TeV)

Reproducción, desde cero, del análisis de **J. Sánchez, *ACI* 15(1) 2780 (2023)** (tesis de maestría USFQ 2022).
El estudio busca vértices desplazados "acausales" (*wrong displaced vertices*) producidos por la desintegración
de un electrón de Lee-Wick, ẽ → e Z, en pp → ẽ⁺ẽ⁻ con Z → jj. La variable clave es la paralelidad transversal
κ∥ = L_T · P_T: si un vértice aparece "antes" de su origen, κ∥ es negativo.

Todo el trabajo se hizo con datos y software públicos: CMS Open Data 2012, CMSSW_5_3_32 en Docker,
FeynRules, MadGraph5_aMC@NLO 3.8.1 y Pythia 8.

## Flujo agéntico

El proyecto está organizado para ejecutarse con agentes de Claude Code. Un coordinador reparte cada etapa
entre agentes especializados, que se pasan el trabajo por archivos con formato fijo. Un verificador independiente
revisa cada entrega, y las decisiones de física las toma la persona en puntos de control.

- `AGENTS.md`: el flujo, los contratos entre agentes y las reglas del coordinador.
- `.claude/agents/`: los 10 agentes (`lector-paper`, `teoria`, `generacion`, `senal-cmssw`, `datos-cms`,
  `fondo-qcd`, `analisis`, `verificador`, `informe`, `vigilante`).
- `EJECUTAR.md`: cómo arrancar un proyecto desde cero y qué mensaje escribir en cada etapa.
- `contratos/`: plantillas del plan y del registro de decisiones.

## Fases

| Fase | Carpeta | Qué hay | Informe |
|---|---|---|---|
| 1. Modelo teórico | `model/`, `validation/` | Lagrangiano en FeynRules (`LWElectron.fr`), UFO, anchos y cτ₀. Coincide con la Tabla 1 del paper en las 6 cifras publicadas. | `docs/fase1_informe.pdf` |
| 2A. Sección eficaz | `generation/xsec/` | σ(pp → ẽ⁺ẽ⁻) a 8 TeV. El paper usa solo intercambio de Z (sin fotón); con γ+Z la σ es 7–10× mayor. | `docs/fase2_informe.pdf`, `docs/fase2_informe_gammaZ.pdf` |
| 2B. Eventos de señal | `generation/events/` | LHE → Pythia → HepMC, con las versiones causal y acausal de los mismos eventos. | `generation/events/README.md` |
| 3A. Señal en CMSSW | `phase3/signal/` | GEN-SIM → HLT con pile-up → RECO → AOD. Usa un `LWMCFileSource` propio (`cmssw/CMSSW_5_3_32/src/LWSim`). | `phase3/signal/README.md` |
| 3B. Análisis | `phase3/analysis/` | `WDVAnalyzer` (v2, convención de la tesis), v3 con mejoras (`mejoras/`) y fondo QCD estimado desde los datos (`qcd/`). | `phase3/analysis/RESULTS.md`, `phase3/analysis/qcd/README.md` |

## Estado (noviembre 2026)

- **Señal:** 2500 colisiones causales con κ → −κ dan 1805 vértices y f(κ∥ < 0) = 0.534, frente a 0.55 en el paper.
  Las colas de la distribución quedan unas 5× por debajo de las del paper.
- **Fondo QCD desde datos** (el MC de 2012 está en cinta): con 2.62 fb⁻¹ (23 % de 2012) se mide R = OS/SS = 1.14 ± 0.06.
  El QCD es ≈ 20 % de los eventos OS y su forma en κ∥ es simétrica (f = 0.48 ± 0.01).
  La fracción de QCD coincide con el paper (28.9 % frente a 29.4 % en vértices).
- **En curso:** la corrida con los 4331 archivos de datos (11.5 fb⁻¹), con `phase3/analysis/qcd/lanzar_todos.sh`.

## Qué no está en el repositorio

Los archivos pesados se regeneran con los scripts y están en `.gitignore`: muestras LHE/HepMC, AOD, pileup,
salidas ROOT, logs, áreas compiladas de CMSSW y directorios de proceso de MadGraph. Las listas de archivos de
CMS Open Data sí están incluidas (`lists*/`, `filelists/`, `meta/`).

## Requisitos

- Docker con la imagen `cmsopendata/cmssw_5_3_32` y acceso por XRootD a `eospublic.cern.ch`
- Wolfram Mathematica con FeynRules 2.3.49 (fase 1)
- MadGraph5_aMC@NLO 3.8.1 y Pythia 8 (fase 2)
- Python 3 con numpy, matplotlib y uproot (gráficos y cálculo QCD)

## Referencias

- J. Sanchez, "Demonstrating the feasibility of testing microscopic acausality at the LHC with CMS open data", *ACI Avances en Ciencias e Ingenierías* 15(1) 2780 (2023): `docs/Sanchez2023_ACI2780.pdf`
- J. J. Sánchez Jácome, "Testing the feasibility to measure wrong displaced vertices from Lee-Wick particle decays with CMS experiment open data", tesis de maestría, USFQ (2022), dir. E. Carrera: `docs/Sanchez2022_tesis_USFQ.pdf`
- E. Álvarez, L. Da Rold, C. Schat y A. Szynkman, "Vertex Displacements for Acausal Particles: Testing the Lee-Wick Standard Model at the LHC", arXiv:0908.2446 (2009): `docs/Alvarez2009_0908.2446.pdf`
- CMS Open Data 2012: <https://opendata.cern.ch>
