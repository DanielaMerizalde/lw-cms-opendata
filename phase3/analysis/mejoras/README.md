# Fase 3 — Estudio de mejoras del método (solo señal simulada)

**Objetivo:** probar si siguiendo a Alvarez et al. (arXiv:0908.2446, Sec. V) el método κ∥ puede distinguir
un decaimiento acausal (WDV) de uno causal. Las pautas son:
- (a) m_jj ≈ m_Z y m_ejj ≈ M_LW;
- (b) dos vértices desplazados correlacionados;
- (c) leptones ℓ̃ muy boosteados y electrones duros;
- (d) un algoritmo de vértices apropiado.

Solo se usó la señal: sólo-Z, M = 200 GeV, 500 eventos causales y 500 acausales reflejados (fase 3A). La v2 no se tocó.

## Código y ejecución

| Archivo | Contenido |
|---|---|
| `src/LWv3/WDVv3/plugins/WDVv3Analyzer.cc` | Selección TF/TO/HQ/JetS idéntica a la v2, sin DRC (DRC se guarda como bandera) |
| `src/LWv3/WDVv3/python/wdv3_cfg.py`, `setup_build.sh` | configuración y compilación |
| `run_v3.sh`, `run_all.sh` | ejecución en el contenedor `lw3b-sig`; los 40 bloques tardan unos 10 min |
| `analyze_v3.py` | evaluación de todas las variantes offline |
| `out/{causal,acausal}/*.root` | ntuples |
| `plots/` | tabla `summary.md` / `summary.json`, `fneg_variants.png/pdf`, `kappa_best.png/pdf`, `kappa_V0.png/pdf`, `masses_truth.png` |

**Qué guarda el ntuple, por evento OS:**
- La verdad de cada ℓ̃: vértice de producción (PV verdadero), vértice de desintegración, electrón y quarks del Z.
- El emparejamiento de los electrones reconstruidos con los electrones de los ℓ̃ (ΔR<0.1, misma carga).
- El emparejamiento de los jets con los quarks (ΔR<0.4).
- Todos los candidatos electrón × par de jets con 50<m_jj<170 GeV, con m_jj, m_ejj y p_T(ejj).
- Para cada candidato, ajustes con 4 limpiezas de trazas × 3 ajustadores.

**Limpiezas de trazas** (la traza del electrón siempre se conserva):

| Código | Trazas eliminadas |
|---|---|
| c0 | ninguna |
| c1 | trazas con peso > 0.5 en cualquier vértice primario (el PV o uno de PU) |
| c2 | trazas de vértices de PU (peso > 0.5) o con significancia de IP transversal respecto del PV < 2 |
| c3 | como c2, con significancia < 3 |

**Ajustadores:**

| Código | Ajustador | Condición de SV bueno |
|---|---|---|
| 0 | SVRA de la v2 (semillas por pares, fusión, Tabla 2.1) | se conservan todos los SV que contienen el electrón |
| 1 | un único ajuste Kalman con todas las trazas del candidato | χ²/ndf<5, ≥3 trazas, contiene el electrón |
| 2 | un único ajuste **adaptativo (AVF)** con todas las trazas | igual que KVF; el AVF reduce el peso de las trazas incompatibles, que es lo que se entiende aquí por "algoritmo de vértices apropiado" |

## Variantes

**V0** — v2:
- SVRA, c0, 80<m_jj<160, corte DRC, L_T>0.02 mm.
- Todos los SV del electrón que cumplen la Tabla 2.1.

**V0'** — V0 sin DRC.

**V1** — asignación de pares:
- En cada evento se asignan pares de jets disjuntos a los dos electrones minimizando
  χ² = ((m_jj−m_Z)/σ_jj)² + ((m_ejj−M)/σ_ejj)².
- Las anchuras salen de los candidatos con verdad correcta: σ_jj = 15.9 GeV (pico en 91.9) y σ_ejj = 16.9 GeV
  (pico en 201.9), calculadas como IQR/1.349.
- **Se usa la hipótesis de masa conocida M = 200 GeV.** En una búsqueda real habría que barrer M.
- Un solo SV por electrón:
  - con SVRA, el de más trazas;
  - con KVF o AVF, el único ajuste.
- No hay corte de L_T.
- Variante adicional: χ²<6 para cada electrón.

**V2** — V1 + los dos electrones deben tener un SV bueno.

**V3** — V1 con limpieza c1, c2 o c3.

**V4** — V1 o V3 más requisitos de desplazamiento o boost:
- L_T/σ_LT > 2 o > 3;
- p_T(ejj) > 100, 150 o 200 GeV;
- p_T(e) > 100 GeV.

## Métricas

Errores binomiales; la correlación entre SV del mismo evento no se tiene en cuenta.

- **ef:** eventos con ≥1 SV seleccionado / 500.
- **verdad A:** el electrón es hijo del ℓ̃ y los dos jets están emparejados con los quarks del Z del **mismo** ℓ̃.
- **verdad B:** |SV − vértice verdadero|_T < 30 µm.
- **f(κ∥<0):** fracción de SV con κ∥<0, con κ∥ = (PV_reco→SV)_T · P_T(trazas del SV), en mm·GeV.
- **sep:** (f_acausal − f_causal) / σ combinada.
- **Δ_T:** mediana de |SV_reco − SV_verdadero|_T, comparada con la mediana de la L_T verdadera.

## Resultados (`plots/summary.md`)

| variante | ef c/a | verdad A | f(κ<0) causal | f(κ<0) acausal | sep | Δ_T / L_T verdadera (µm) |
|---|---|---|---|---|---|---|
| V0 (v2) | 0.12/0.13 | 0.13 | 0.53±0.03 | 0.52±0.03 | −0.3σ | 44 / 15 |
| V0' (sin DRC) | 0.33/0.33 | 0.14 | 0.49±0.02 | 0.54±0.02 | 2.1σ | 40 / 16 |
| V1 SVRA | 0.36/0.36 | 0.53 | 0.37±0.03 | 0.65±0.03 | 7.3σ | 24 / 14 |
| V1 AVF | 0.26/0.27 | 0.56 | 0.32±0.04 | 0.69±0.03 | 7.5σ | 20 / 15 |
| **V1 AVF + χ²<6** | 0.23/0.24 | 0.63 | **0.31±0.04** | **0.72±0.04** | **7.6σ** | 20 / 15 |
| V2 (AVF, ambos e) | 0.08/0.09 | 0.61 | 0.24±0.05 | 0.73±0.05 | 7.4σ | 21 / 17 |
| V3 AVF c1 / c2 / c3 | 0.14 / 0.06 / 0.02 | 0.6–0.7 | 0.51 / 0.44 / 0.33 | 0.62 / 0.65 / 0.67 | 1.4–1.7σ | 60–85 / 16–25 |
| V4 V1 AVF + L_T/σ>2 | 0.08/0.08 | 0.67 | 0.19±0.06 | 0.81±0.06 | 7.5σ | 27 / 28 |
| V4 V1 AVF + p_T(ejj)>150 | 0.14/0.15 | 0.63 | 0.29±0.05 | 0.72±0.05 | 6.5σ | 20 / 22 |

## Conclusiones

1. **La combinatoria era el problema principal, y la pauta (a) de Alvarez lo resuelve en buena medida.**
   - Asignar a cada electrón el par de jets compatible con m_Z y M_ℓ̃ sube la fracción de candidatos correctos
     de 14 % a 53–63 %.
   - La resolución del vértice baja de ~40 a ~20 µm.
   - f(κ<0) pasa de 0.53 frente a 0.52 (sin separación) a 0.31 (causal) frente a 0.72 (acausal), unas 7.5σ con
     500 + 500 eventos.
   - El "flip" de la tesis ya no hace falta para ver la asimetría: la muestra reflejada la muestra directamente.

2. **El algoritmo de vértices apropiado ayuda un poco.**
   - El AVF con todas las trazas del candidato da una resolución algo mejor que la SVRA (20 frente a 24 µm) y un
     candidato más limpio.
   - Un KVF sin pesos falla casi siempre (χ²>5), por las trazas incompatibles.

3. **La limpieza de trazas empeora el resultado.**
   - El desplazamiento verdadero (mediana ~15 µm en L_T) es menor que la resolución del PV y del IP.
   - Por eso las trazas de la señal son compatibles con el PV, y se eliminan junto con las de PU.
   - La eficiencia cae a 2–14 %, la resolución a 60–85 µm y la separación a ~1.5σ.
   - **Para M = 200 GeV en CMS 2012 no se debe limpiar por compatibilidad con el PV.**

4. **El boost y la significancia de desplazamiento (pauta c) aumentan la asimetría por vértice, a costa de eficiencia.**
   - Con L_T/σ>2: f(κ<0) es 0.19 frente a 0.81, con eficiencia del 8 %.
   - Con p_T(ejj)>150: 0.29 frente a 0.72, con eficiencia del 14 %.

5. **Dos vértices correlacionados (pauta b):** exigir SV en los dos electrones (V2) apenas mejora la asimetría y
   divide la eficiencia por 3. Se puede dejar para una etapa posterior.

6. **Límite irreducible.**
   - Aun en el mejor caso, Δ_T ≈ 20 µm es mayor que la L_T verdadera mediana (~15 µm).
   - La asimetría viene de la cola de eventos con desplazamiento grande. Para M = 200 GeV, el boost
     (⟨βγ_T⟩ ≈ 0.7) no basta para alcanzar los 20 µm en la mayoría de los eventos. Alvarez exige
     p_T(ℓ̃) ≳ M·Δx·Γ, lo que deja una fracción pequeña.
   - Con 11.5 fb⁻¹ la señal esperada es ~4–8 eventos tras la selección (σ×L×ef). Por eso la sensibilidad en datos
     depende sobre todo del fondo, que aquí no se evaluó.

## Advertencias

- Solo se usó señal. Falta comprobar que en el fondo (DY, tt̄, QCD en datos SS) f(κ<0) ≈ 0.5 con V1. Los fondos
  con vértices causales reales, como los b de tt̄, deberían dar f<0.5.
- La χ² usa la masa verdadera de la muestra (M = 200 GeV).
- Las anchuras σ se toman de la propia señal; con la estadística disponible no se separan los conjuntos de
  entrenamiento y evaluación. El sesgo debería ser pequeño, porque solo intervienen dos parámetros por masa.
- Los errores binomiales por SV ignoran la correlación entre SV del mismo evento. En V1 hay como mucho dos SV por
  evento, así que el efecto es pequeño.

## Recomendación

Para aplicar a datos y fondo, usar **V1 con AVF y χ²<6 por electrón**, sin DRC, sin IPP y sin limpieza:
- κ∥ = (PV→SV)_T · P_T(trazas).
- Como selección más estricta, añadir L_T/σ>2 (o p_T(ejj)>150).
- La observable es f(κ<0) en datos frente al fondo, y no el "flip".
