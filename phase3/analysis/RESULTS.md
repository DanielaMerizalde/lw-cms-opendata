# Fase 3B — Resultados (analizador v2, convención de la tesis USFQ 2022)

**Fecha:** 21-10-2026.
**Código:** `src/LWAnalysis/WDVAnalyzer/` y `plot_v2.py`. Diagnósticos en `investigate_signal.py`, `ipp_variants.py` e `ipp_units.py`.
**Decisiones y desviaciones:** ver `README.md` (sección v2).

## 1. Qué se procesó

**Datos:**
- 43 archivos completos elegidos al azar (16 de Run2012B y 27 de Run2012C), con 610 987 eventos leídos tras el JSON certificado.
- Luminosidad: **L ≈ 112.8 pb⁻¹** por fracción de bytes, es decir **0.98 %** de 11.467 fb⁻¹. La estimación por lumisecciones da 117.9 pb⁻¹.

**MC:**
- **Solo 1 archivo por muestra:** DY 11 474 ev, TT 5 992 (Σ signos = 3 590), W1 8 359, W2 12 082, W3 7 657.
- Los registros MC de 2012 tienen **un solo archivo online**; el resto está en cinta ("on demand") y habría que pedir que lo restauren desde el portal.
- Consecuencia: en SG solo quedan 8 eventos DY y 7 TT. Con peso ≈ 34 por evento, la estadística del fondo MC es del orden de ±35–40 %, y W+jets queda en 0.

**Señal (fase 3A):**
- Sólo-Z, M = 200 GeV: 11 bloques causales (275 ev) y 10 acausales reflejados (250 ev).
- Normalización: σ = 5.97 fb. En nuestra convención se multiplica por BR(Z→had)² = 0.4887; en la de la tesis no (Z forzado a quarks; su NF = 67.7 ≈ 5.97 fb × 11.3 fb⁻¹).

## 2. Cutflow frente a la Tabla 2.2 de la tesis

El detalle completo está en `plots/cutflow_v2.md`: conteos escalados a 11.467 fb⁻¹, eficiencias y conteos crudos.

**Eficiencia relativa al corte anterior (nuestra / tesis):**

| corte | Datos | DY | TTbar | LW200 causal | LW200 acausal |
|---|---|---|---|---|---|
| TF | 0.057 / 0.088 | 0.059 / 0.098 | 0.011 / 0.011 | 0.67 / 0.76 | 0.67 |
| TO | 0.71 / 0.40 | 0.85 / 0.51 | 0.75 / 0.53 | 0.86 / 0.56 | 0.90 |
| HQ | 0.87 / 0.97 | 0.95 / 0.98 | 0.97 / 0.98 | 0.99 / 0.99 | 0.95 |
| JetS | 0.063 / 0.031 | 0.055 / 0.019 | 0.28 / 0.27 | 0.62 / 0.40 | 0.55 |
| DRC | 0.24 / 0.99 | 0.27 / 0.98 | 0.75 / 0.93 | 0.36 / 0.94 | 0.35 |
| SG | 0.86 / 0.71 | 1.0 / 0.85 | 0.83 / 0.74 | 0.97 / 0.97 | 1.0 |
| IPP | 0.39 / 0.003 | 0.62 / 0.0003 | 0.80 / 0.008 | 0.56 / 0.0023 | 0.57 |

**Conteos crudos de datos (OS):** 610 987 → 34 992 → 24 724 → 21 415 → 1 343 → 317 → 271 → 105.

**Región SS (QCD):** 46 eventos en SG y 14 en IPP. Escalados a la luminosidad completa, QCD = datos_SS − MC_SS da 3 956 en SG (tesis: 1 665) y 1 423 en IPP (tesis: 55).

**Escalados a 11.467 fb⁻¹:** en datos, SG = 2.76×10⁴ (tesis 4.89×10⁴). Para LW200 en SG: 4.1 eventos (×BR²) y 8.5 eventos sin BR (tesis: 10.4).

**Lectura:**
- TF y HQ son comparables.
- TO es menos restrictivo en nuestro análisis: emparejamos con objetos de trigger del último filtro.
- JetS es el doble de eficiente.
- **DRC es la gran diferencia:** en la tesis prácticamente no corta (≈0.98), mientras que aquí deja pasar ≈25 % en el fondo y 36 % en la señal. Con la definición escrita (|ΔR1−ΔR2|<0.2 con los jets seleccionados) no se puede obtener una eficiencia de 0.98. La tesis debió de usar otra definición, quizá con todos los jets o con todas las combinaciones de electrón.
- La eficiencia de SG en datos (0.86 frente a 0.71) indica una componente de mismo signo (QCD) menor que la de la tesis.

## 3. κ∥ (Fig. 2.5)

**Figuras:**
- `plots/kappa_fig2p5_k_r150.png/.pdf`, en el rango de la tesis.
- `plots/kappa_fig2p5_k_r20.png/.pdf`, ampliado a ±20 mm·GeV, donde está casi todo.

**Contenido de los histogramas:**
- κ∥ = (PV→SV)_T·P_T, con P_T de las trazas del SV.
- Etapa SG, con los SV que tienen L_T > 0.02 mm.
- Datos: 442 SV, todos con |κ∥| ≲ 50 mm·GeV.
- Fondo: DY 655, TT 57, QCD (SS) 69–90, W 0; **datos/fondo = 0.56**.
  - DY son 23 SV crudos con peso ≈ 34, así que su incertidumbre estadística es de ≈ ±25–35 %. Más la sistemática del 19 %, la discrepancia es de ~1.5–2σ.
- Fracción con κ∥<0: datos OS 0.527 ± 0.024; datos SS 0.49 ± 0.05. Es simétrico, como se espera del fondo.

**Señal (×1000):**
- Esperado a 112.8 pb⁻¹ en SG: 0.17 SV en la muestra causal y 0.19 en la acausal (×BR²).
- A la luminosidad completa se esperan ~17–19 SV (×BR²) o ~36–40 SV sin BR, frente a ~4.5×10⁴ SV en datos (~8×10⁴ de fondo estimado).

## 4. Señal: flip frente a reflexión (`plots/signal_flip_vs_reflect_k_r20.png`)

Fracción de SV con κ∥<0 (etapa SG, L_T>0.02 mm; error binomial, que subestima la incertidumbre porque los SV del mismo evento están correlacionados):

| muestra | todos los SV | SV emparejados con el vértice verdadero |
|---|---|---|
| causal, tal cual | 0.58 ± 0.04 (N=142) | 0.25 ± 0.11 (N=16) |
| causal con flip de la tesis | 0.42 ± 0.04 | 0.75 |
| acausal reflejada | 0.51 ± 0.04 (N=144) | **0.92 ± 0.06 (N=24)** |

## 5. Preguntas investigadas

**(1) Eficiencia IPP de la señal: 56–57 % aquí frente a 0.23 % en la tesis (0.024/10.4).**
- Nuestro IPP es la lectura literal: algún SV con κ∥<0 y |P_T|>20 GeV, y todos los *demás* SV de ese electrón con L_T>0.02 mm.
- Con ~3.3–4.3 SV por electrón y ~56–60 % de SV con L_T>0.02 mm, esa condición se cumple a menudo. Además, un electrón con un único SV solo necesita κ∥<0.
- Variantes probadas (`plots/ipp_variants.json`, `plots/ipp_units.json`):

| variante | eficiencia señal | eficiencia datos |
|---|---|---|
| todos los SV del electrón, incluido el candidato, con L_T>0.02 | 44–46 % | 24 % |
| todos los SV del *evento* con L_T>0.02 | 12–14 % | 12 % |
| corte de 0.02 aplicado en cm (= 0.2 mm, posible error de unidades de CMSSW) | 4–6 % | 15 % |

- **Ninguna lectura razonable reproduce eficiencias de ~0.3 %** para todas las muestras a la vez (datos 0.003, DY 0.0003, TT 0.008, señal 0.0023).
- Una eficiencia tan baja y casi igual en señal y fondo indica que la tesis tenía muchos más SV por electrón, por ejemplo sin aplicar la Tabla 2.1 antes del IPP o sin eliminar duplicados entre pares de jets, o una condición adicional que no está escrita. **No es reproducible con lo publicado.**
- Con el IPP de la tesis, la señal final esperada sería 0.024 eventos: el corte final no tenía poder práctico.

**(2) Por qué la muestra acausal no muestra más SV con κ∥<0 que la causal.**
- **Las convenciones son correctas.** κ∥ de verdad, calculado como (vértice generado del e − PV reconstruido)_T·p_T(e), da f(κ<0) = 0.22 ± 0.05 en la causal y 0.73 ± 0.06 en la acausal. El signo de la reflexión y la elección del PV funcionan. No da 0/1 porque la resolución del PV es comparable al desplazamiento verdadero, y porque el electrón no va exactamente en la dirección de ℓ̃.
- **El problema es la resolución:**
  - El desplazamiento transversal verdadero tiene mediana de 0.021 mm (causal) y 0.017 mm (acausal), con λ ≈ 27 µm.
  - La distancia entre el SV reconstruido y el vértice verdadero tiene mediana de 0.045–0.053 mm, mayor que el propio desplazamiento.
  - Solo el **14–17 % de los SV** está más cerca del vértice verdadero que la mitad del desplazamiento.
  - En esos SV emparejados, κ∥ tiene el signo correcto: 75 % positivo en la causal y **92 % negativo en la acausal**.
  - El resto son combinaciones electrón+par de jets con trazas de PU o del otro ℓ̃, y diluyen la asimetría hasta ~50 %.
- Todos los SV guardados contienen la traza del electrón de señal (sv_sig = 1). Por eso el emparejamiento electrón–verdad no es el problema; lo es la posición del vértice.
- Consecuencia: el "flip" de la tesis no reproduce lo que hace un WDV verdadero. En la muestra causal reconstruida no hay una asimetría positiva clara (0.42 de κ<0, no ≪0.5), así que invertir el signo solo traslada fluctuaciones. La muestra reflejada da 0.51.
- Una asimetría como la de la Fig. 2.5 solo aparecería si la mayoría de SV fueran correctos. Eso requiere identificar los jets del Z y aplicar cortes de calidad de vértice más fuertes, cosa que la tesis también reconoce.

**(3) Por qué JetS y DRC difieren entre causal y acausal para "los mismos" eventos.**
- En los 10 bloques comunes el cutflow es causal 250/165/141/139/83/30/29/19 frente a acausal 250/168/152/145/79/28/28/16. La diferencia en JetS (83 frente a 79) y en DRC (30 frente a 28) es estadística.
- La aparente diferencia 0.62 frente a 0.55 en JetS incluía el bloque causal b010, que no tiene pareja.
- A nivel de evento las muestras se descorrelacionan después del GEN: al mover el vértice de decaimiento cambian Geant4 (trazas, interacciones, secuencia aleatoria), la digitización y la reconstrucción. De los 30 y 28 eventos que pasan DRC, solo 19 son comunes.

## 6. Advertencias principales

- **MC limitado a 1 archivo por muestra.** El fondo simulado no tiene estadística después de JetS, y W+jets es 0. La comparación absoluta datos/MC (0.56) no es concluyente.
- **Las eficiencias por corte son lo comparable.** DRC e IPP no reproducen la tesis, ni siquiera cualitativamente.
- La luminosidad es aproximada (sin brilcalc). La fila NF de datos escalada (6.2×10⁷ frente a 6.6×10⁷) es menor porque NF se cuenta después del JSON.
- QCD se obtiene de SS con R_OS/SS = 1. La señal sigue siendo pequeña (21 bloques, unos 525 eventos); la producción continúa en la fase 3A.
- Sin PU-reweighting ni factores de escala, como en la tesis.

## Actualización 2026-10-25: señal completa (40/40 bloques, 500 causales + 500 acausales)

| | causal | acausal |
|---|---|---|
| Cutflow NF/TF/TO/HQ/JetS/DRC/SG/IPP | 500/337/290/286/187/70/67/36 | 500/349/311/300/189/70/70/37 |
| f(κ∥<0), todos los SV (L_T>0.02 mm, etapa SG) | 0.53 ± 0.03 (N=327); con flip de la tesis 0.47 | 0.51 ± 0.03 (N=330) |
| f(κ∥<0), SV sobre la desintegración verdadera | 0.24 ± 0.06 (N=51) | 0.86 ± 0.05 (N=51) |
| Fracción de SV emparejados con la verdad | 15.6 % | 15.5 % |

Conclusiones sin cambios respecto a 21 bloques: la variable discrimina cuando el SV es correcto, pero la combinatoria electrón + par de jets diluye la asimetría. Gráficas con 21 bloques en plots_21bloques/.

## v3 final (2026-10-27): método mejorado aplicado a datos, fondos y señal

Selección: v2 sin DRC ni IPP + asignación χ² (m_jj≈91, m_ejj≈200, pares disjuntos, χ²<6) + ajuste adaptativo. 43 archivos de datos (≈113 pb⁻¹), 1 archivo por fondo, 500+500 señal. Detalle: mejoras/plots_final/ (cutflow_v3final.md, numbers_v3final.json, fig2_paper_vs_v3.png).

| f(κ∥<0), L_T>0.02 mm | valor |
|---|---|
| Datos (89 SV) | 0.54 ± 0.05 |
| QCD (datos SS, 35 SV) | 0.46 ± 0.08 |
| Señal causal / causal con flip / acausal reflejada | 0.25 / 0.76 / 0.79 (± 0.05) |

¿Se reproduce la Fig. 2? Cualitativamente sí (datos simétricos, señal inclinada a κ<0; flip y reflexión coinciden ahora); la forma no (sin colas hasta ±150: las producían combinaciones falsas). Fondo MC sin estadística (1 DY y 1 tt̄ pasan L_T>0.02). Señal esperada en 11.47 fb⁻¹ tras selección: ~4–5 eventos (σ del paper ×BR²).
