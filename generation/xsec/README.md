# Fase 2A: sección eficaz σ(pp → ẽ⁺ẽ⁻) a √s = 8 TeV

Objetivo: reproducir la Tabla 1 de Sánchez, ACI 15(1) 2780 (2023):
M = 200, 300, 400, 500 GeV → σ = 5.97, 0.96, 0.23, 0.06 fb (el artículo escribe "fb⁻¹", pero son fb).
Buscamos qué elección de modelo, PDF y escala reproduce esos números.

## Resultado principal

**La Tabla 1 se reproduce al ~1 % (M = 200–400) solo si se quita el intercambio de fotón**: `p p > z > elw+ elw-`,
con `lwRep = 0` (Ec. 1 literal), la PDF por defecto de MG5 (NNPDF2.3 LO, `nn23lo1`) y la escala dinámica por defecto (`-1`).
Con el modelo físico (γ + Z), σ es **7–10 veces mayor** que en el artículo.

| M (GeV) | Artículo | **solo Z, lwRep=0, NNPDF2.3LO** | cociente | γ+Z, lwRep=0 (físico) | γ+Z, lwRep=1 (doblete) |
|---|---|---|---|---|---|
| 200 | 5.97 | **5.950** (+4.4/−4.2 %) | 0.997 | 42.30 (+3.7/−3.2 %) | 77.05 |
| 300 | 0.96 | **0.958** (+6.4/−5.9 %) | 0.998 | 7.530 (+5.7/−5.2 %) | 13.65 |
| 400 | 0.23 | **0.2274** (+8.3/−7.1 %) | 0.989 | 1.943 (+7.1/−6.6 %) | 3.528 |
| 500 | 0.06 | **0.0668** (+9.4/−8.2 %) | 1.114 | 0.6136 (+8.6/−7.6 %) | 1.115 |

Todo es σ en fb, a LO. El error estadístico de MG es ≈ 0.1–0.15 %. Entre paréntesis va la variación de escala
(μ_R = μ_F a la vez, ×2 y ×0.5). El punto M = 500 queda 11 % alto: 0.0668 redondearía a 0.07, no a 0.06.
No encontramos ninguna opción que corrija solo ese punto (ver abajo). Puede venir de otra versión de MG o de la estadística del artículo, pero no lo sabemos.

Gráfico: `xsec_vs_M.png`. El panel de arriba muestra σ(M). El del medio, σ/σ_artículo. El de abajo compara la dependencia en M:
[σ(M)/σ(200)]/[ídem artículo], que no depende de la normalización y casi no depende de PDF ni de escala.
**Dependencia en M**: el artículo da (1, 0.161, 0.0385, 0.0101).
"Solo Z, NNPDF" da (1, 0.161, 0.0382, 0.0112). Cualquier configuración con fotón da (1, 0.178, 0.046, 0.0145), más plana que el artículo,
para todas las PDFs y escalas probadas. Esto descarta "γ+Z × un factor constante" (BR, cortes, quiralidad...) como explicación.

## Método

- MG5_aMC 3.8.1, UFO `model/LWElectron_UFO` (fase 1, sin modificar). `import model <ruta absoluta>`.
- Procesos (directorios `proc_*`):
  - `proc_full`: `p p > elw+ elw-` (γ y Z en canal s). `p` = g u c d s ū c̄ d̄ s̄ (4 sabores, b masivo en el UFO).
  - `proc_full5f`: `p5 p5 > elw+ elw-` con `p5 = p b b~`: +0.6 % (200 GeV), +0.2 % (500 GeV). Despreciable.
  - `proc_aonly`: `p p > a > elw+ elw-`, y `proc_zonly`: `p p > z > elw+ elw-`.
  - `proc_chainjj`: `p p > elw+ elw-, (elw+ > e+ z, z > j j), (elw- > e- z, z > j j)` (cadena del artículo, Z → jj).
- Cartas: `ebeam = 4000`, 10 000 eventos por punto, `etaLW = +1`, `MeLW = 5e-4`, `WLW` = ancho de fase 1 para cada M, sin shower.
- PDFs: `nn23lo1` (defecto de MG ≥ 2.x), CTEQ6L1 (`lhaid 10042`, defecto de CMS/MadGraph en 2012), MSTW2008lo68cl (`lhaid 21000`).
- Escalas: dinámica por defecto `-1`, `3` (H_T/2), `4` (√ŝ), y fijas μ = M y μ = 2M. Para la incertidumbre, `scalefact = 0.5, 2`.
- **Chequeo analítico independiente** (`analytic_check.py`): fórmula LO de q q̄ → γ*/Z* → F F̄ masivo, integrada con la rejilla CTEQ6L1 leída directamente.
  A μ_F = √ŝ coincide con MG al 0.1 %. Por ejemplo, para M = 200, γ+Z lwRep=0: 44.37 (analítico) vs 44.37 (MG `dyn4`) y 44.30 (MG `-1`).
  Para lwRep=1: 80.39 vs 80.34. Para solo Z: 6.271 vs 6.273. Así se confirma que el UFO y MG están bien: la diferencia con el artículo no es un error nuestro.

## Qué se probó (σ/σ_artículo en M = 200 … 500)

| Configuración | 200 | 300 | 400 | 500 | ¿forma OK? |
|---|---|---|---|---|---|
| γ+Z, lwRep=0, NNPDF, dyn | 7.09 | 7.84 | 8.45 | 10.2 | no |
| γ+Z, lwRep=0, CTEQ6L1, dyn / μ=M / μ=2M / H_T/2 / √ŝ | 7.42 / 7.87 / 7.60 / 7.74 / 7.43 | 8.5–9.2 | 9.3–10.3 | 11.4–12.8 | no |
| γ+Z, lwRep=0, MSTW08LO | 7.57 | 8.78 | 9.76 | 12.1 | no |
| γ+Z, lwRep=1 (doblete), NNPDF / CTEQ / MSTW | 12.9 / 13.5 / 13.7 | 14.2–15.8 | 15.3–17.5 | 18.6–21.7 | no |
| solo γ | 5.88 | 6.64 | 7.19 | 8.82 | no |
| **solo Z, lwRep=0, NNPDF** | **0.997** | **0.998** | **0.989** | **1.114** | **sí** |
| solo Z, lwRep=0, CTEQ6L1 (dyn / μ=M / μ=2M) | 1.05 / 1.14 / 1.09 | 1.08–1.21 | 1.09–1.24 | 1.23–1.42 | casi |
| solo Z, lwRep=0, MSTW08LO | 1.07 | 1.10 | 1.12 | 1.27 | casi |
| solo Z, lwRep=1, NNPDF | 3.51 | 3.78 | 4.02 | 4.82 | no |
| γ+Z × BR(Z→jj)² (cadena MG, j de 4 sabores, sin cortes) | 1.76 | – | – | – | – |
| γ+Z × BR(Z→jj)² + cortes por defecto de MG (`cut_decays = T`) | 0.857 | – | – | 1.58 | **no** |
| Analítico (CTEQ6L1, √ŝ): solo ẽ_R (γ+Z) / solo ẽ_L (γ+Z) | 1.92 / 4.46 | 2.17 / 4.98 | 2.36 / 5.38 | 2.86 / 6.49 | no |
| Analítico: solo ẽ_R sin γ / solo ẽ_L sin γ | 0.93 / 1.21 | 1.01 / 1.31 | 1.08 / 1.40 | 1.29 / 1.67 | no |
| Analítico: γ+Z a 7 TeV / solo Z a 7 TeV | 5.72 / 0.79 | 6.13 / 0.76 | 6.30 / 0.71 | 7.20 / 0.74 | no |

Otros chequeos:
- `etaLW = −1` vs `+1`: 42.43 vs 42.30 fb (1.8σ estadístico). Es una fase global y analíticamente σ es idéntica.
- μ_R solo (μ_R = 2 TeV fijo): 42.38 vs 42.30 fb, sin efecto. A LO el proceso es puramente EW (no hay α_s), así que solo cuenta μ_F.
- Interferencia γ–Z: con lwRep=0 es pequeña, +1.2 fb (3 %) a 200 GeV (42.30 = 35.11 + 5.95 + 1.24), porque el acoplamiento vectorial de ẽ al Z, −1/2 + 2s_W², es casi cero.
  Con lwRep=1 es grande y constructiva, +20.9 fb (77.05 = 35.15 + 20.97 + 20.93). Por eso lwRep=1 da σ ≈ 1.8 × lwRep=0.
- La cadena con Z → jj: BR(Z → jj, 4 sabores, LO) = √(10.52/42.30) = 0.499. Con los cortes por defecto de MG se acerca en M = 200 (5.12 fb) por casualidad.
  Pero la eficiencia de los cortes crece con M, así que la forma empeora (0.095 fb a 500 GeV, 1.6 × el artículo). Queda descartado.

**Interpretación.** Lo más probable es que el modelo FeynRules del artículo implementara solo el Lagrangiano de corriente neutra de la Ec. (1) (acoplamientos ẽẽZ y mezcla)
con un término cinético sin derivada covariante. Así, ẽ no se acopla al fotón. Eso coincide en normalización y forma con la PDF y la escala por defecto de MG5 2.x/3.x.
Una partícula con Q = −1 sin acoplamiento al fotón no es físicamente consistente (rompe la invariancia gauge U(1)_em).

## Incertidumbres

- Escala (μ_F ×2, ×0.5): ±4 % (200 GeV) a ±9 % (500 GeV), casi igual para todas las configuraciones (ver `scale_up_rel` y `scale_down_rel` en `xsec.csv`).
- PDF (dispersión entre conjuntos LO, NNPDF2.3 vs CTEQ6L1 vs MSTW08): +5–7 % (200 GeV) a +10–18 % (500 GeV) respecto de NNPDF. Es mayor que la de escala a M alta.
  No se calcularon réplicas PDF: el módulo `systematics` no funciona aquí (ver abajo).
- NLO: no incluido. Un factor K típico de Drell-Yan es ≈ 1.2–1.3.

## Recomendación para el análisis

1. **Normalización.**
   - Para *reproducir el artículo*, hay que usar σ del artículo (5.97, 0.96, 0.23, 0.06 fb). Equivale a nuestro "solo Z, lwRep=0, NNPDF2.3LO".
     Para M = 500 recomendamos 0.0668 fb (nuestro valor) en lugar de 0.06, o al menos anotarlo como sistemático.
   - Para un resultado *físicamente correcto*, hay que usar γ+Z con lwRep=0: **42.3, 7.53, 1.94, 0.614 fb** (NNPDF2.3LO, LO). Son ×7.1 (200 GeV) a ×10 (500 GeV) respecto del artículo.
     Recomendamos dar ambos: el principal para reproducir y el físico como comparación. Ese factor ~7 aumenta en la misma proporción la sensibilidad esperada.
2. **lwRep = 0.** Es la Ec. (1) literal y la única que, sin fotón, reproduce la tabla. lwRep=1 queda excluido como lo que usó el artículo (3.5–4.8 veces su valor en la versión solo Z).
   lwRep=1 sigue siendo la opción teóricamente motivada (socio vectorial del doblete, Alvarez et al.). Si se estudia, da σ ≈ 1.8 veces la de lwRep=0 con fotón.
3. **PDF y escala.** `nn23lo1` y `dynamical_scale_choice = -1` (defectos de MG). CTEQ6L1 no mejora el acuerdo: queda 5–22 % alto.
4. **Generación de eventos.** Las formas cinemáticas de "solo Z" y "γ+Z" son casi iguales (s-canal vectorial en ambos casos; difieren en la asimetría angular).
   Es razonable generar con el modelo completo γ+Z, lwRep=0 y normalizar con σ del artículo para la reproducción. Esto no se verificó aquí con distribuciones.

## Problemas y advertencias

- **Binding python de LHAPDF roto.** `lhapdf.so` está compilado para py3.11. Con el python 3.12 por defecto falla, y con el python 3.11 del entorno `mg5` hace segfault (doble libpython).
  Por eso no funciona el módulo `systematics` de MG: las variaciones de escala se hicieron con corridas separadas (`scalefact`) y no hay incertidumbre PDF por réplicas.
- **MSTW2008lo68cl.** La interfaz Fortran de MG pedía `AlphaS_Lambda4`, que falta en el `.info`. Se añadieron valores de relleno (`AlphaS_Lambda4/5`) en
  `MG5_aMC_v3_8_1/bin/HEPTools/lhapdf6_py3/share/LHAPDF/MSTW2008lo68cl/MSTW2008lo68cl.info` (el original queda en `.info.orig`). α_s no entra en σ a LO.
- MG guardó `lhapdf_py3 = .../bin/HEPTools/lhapdf6_py3/bin/lhapdf-config` en `MG5_aMC_v3_8_1/input/mg5_configuration.txt` (lo hace `set lhapdf_py3`). Antes apuntaba a una ruta que no existía.
  MG descargó CTEQ6L1 y MSTW2008lo68cl del servidor oficial de LHAPDF.
- La cadena `proc_chainjj` recompila 64 subprocesos en cada `launch` (~30 min por punto con la máquina cargada). Solo se corrió en M = 200 y 500.
- MG avisa de "small width" para ẽ (Γ ~ 1e-11 GeV). No afecta a σ de producción.

## Archivos

| Archivo | Qué es |
|---|---|
| `run_xsec.py` | Driver: define todas las corridas (grupos base, pdf, diag, 5f, chain, zbest), las lanza en paralelo en copias temporales `proc_*_slot*` (ya borradas) y escribe `results_raw.csv`. Es incremental: salta corridas ya hechas y recupera resultados de los logs. |
| `make_table.py` | `results_raw.csv` → `xsec.csv` + `xsec_vs_M.png` |
| `analytic_check.py` | Cálculo analítico independiente (log en `logs/analytic_check.log`) |
| `xsec.csv` | config (`proceso|PDF|lwRep|escala[|extra]`), M, σ (fb), error estadístico, variación de escala relativa arriba/abajo, σ/σ_artículo |
| `results_raw.csv` | Todas las corridas, incluidas las variaciones `sf = 0.5, 2` |
| `scripts/` | Scripts `.mg5`: generación de procesos (`gen_procs.mg5`, `gen_chain.mg5`) y lanzamientos (`runs/*.mg5`, `launch_*.mg5`) |
| `logs/` | Logs de MG (`runs/` = una sesión por corrida) y del driver |
| `proc_*/` | Directorios de proceso MG con cartas y banners de cada corrida (`Events/<run>/*banner.txt`) |

Reproducir: `python3 run_xsec.py` (≈ 1.5 h en 8 núcleos) y luego `python3 make_table.py`.
