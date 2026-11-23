# Fase 2B: eventos de señal a nivel generador con vértices desplazados (causales y acausales)

Reproducción de J. Sánchez, *ACI* **15**(1) 2780 (2023). Aquí se genera la señal
pp → ẽ⁺ẽ⁻ → (e⁺Z)(e⁻Z), Z → jj a √s = 8 TeV con la longitud de vuelo correcta del ẽ.
Se implementa la geometría **acausal** (WDV, *wrong displaced vertex*) y se estudian a nivel de verdad
el desplazamiento, la paralelidad κ∥ y las masas invariantes. No hay simulación de detector (eso es la fase 3,
CMSSW_5_3_32). Los archivos HepMC están pensados para que la fase 3 los use directamente.

## 1. Qué se generó

| M (GeV) | cτ₀ (μm) | eventos | σ·BR(Z→had)² MG5 LO (fb) | archivos (`samples/M*/`) |
|---|---|---|---|---|
| 200 | 27.08 | 20 000 | 17.22 | `lw_M200.lhe.gz`, `lw_M200_causal.hepmc.gz`, `lw_M200_acausal.hepmc.gz`, `truth_M200_{elw,jets}.csv` |
| 300 | 16.43 | 5 000 | 3.057 | ídem |
| 400 | 12.12 | 5 000 | 0.793 | ídem |
| 500 | 9.65 | 5 000 | 0.2505 | ídem |
| 200, lwRep=1 | 27.08 | 20 000 (solo LHE) | 31.26 | `mg5/PROC_lw_ejj/Events/M200_lwRep1/` |

Las secciones eficaces son solo informativas: PDF `nn23lo1`, escala dinámica por defecto de MG5 y sin cortes.
El cálculo de σ lo hace otro agente en `generation/xsec/`. Tamaño en disco: unos 3.2 GB, casi todo HepMC (≈47 kB/evento comprimido).

### Cadena
1. **MG5_aMC 3.8.1** (`mg5/`). Se usa una copia del UFO de la fase 1 (`mg5/ufo/LWElectron_UFO`); `model/` no se toca.
   La copia lleva una tarjeta de restricción `restrict_lwcms.dat` que pone a cero las masas y Yukawas de u, d, s, c, e y μ,
   para tener un protón de 4 sabores sin masa. b y t siguen siendo masivos.
   Los valores de `etaLW` y `lwRep` en la tarjeta de restricción (0.77 y 0.123) no tienen significado: solo sirven
   para que MG5 no los fije a 0 o 1 y sigan siendo parámetros libres. Los valores de verdad están en las param_cards.
   ```
   define p  = g u c d s u~ c~ d~ s~
   define qz = u c d s b u~ c~ d~ s~ b~        # Z -> hadrones INCLUYENDO b b~
   generate p p > elw+ elw-, (elw+ > e+ z, z > qz qz), (elw- > e- z, z > qz qz)
   ```
   - **Sintaxis de cadena de desintegración en vez de MadSpin.** El elemento de matriz completo 2→6 se evalúa en la
     aproximación de anchura estrecha con todas las helicidades propagadas, así que las correlaciones de espín
     producción–desintegración (ẽ y Z) son exactas a LO. Además no hace falta una tarjeta de MadSpin para una partícula
     con Γ ~ 10⁻¹¹ GeV. MG5 maneja la anchura minúscula con `small_width_treatment` (aviso "small width detected"):
     integra con una anchura regularizada y reescala σ. La cinemática es on-shell.
   - **Tarjetas.** `mg5/make_cards.py` escribe `cards/param_card_M*.dat` con MeLW = 5·10⁻⁴, **etaLW = +1**, lwRep = 0 y
     WLW = Γ_FR de la fase 1. El script `mg5/run_mg5.sh M N SEED` lanza la generación con
     `time_of_flight = 0` (escribe VTIMUP para toda partícula con anchura: cτ propio muestreado de una exponencial, en mm),
     sin ningún corte de generador (ptj = ptl = 0, sin η, sin ΔR) y `cut_decays = False`.
     Las semillas son 2002 (M = 200), 3003, 4004, 5005 y 2012 (lwRep = 1).
2. **Pythia 8.317** (`pythia/`). El driver propio `lw_pythia_hepmc.cc` (compilar con `build.sh`) usa la tarjeta
   `lw_8TeV_CUETP8M1.cmnd`:
   - `LesHouches:setLifetime = 1`: Pythia toma el VTIMUP del LHE.
   - `Tune:pp = 18`: **CUETP8M1** (MonashStar, NNPDF2.3 LO). Ojo: CMS 2012 usó Pythia6 Z2*; no hay Z2* para Pythia8.
   - MPI, ISR y FSR activados.
   - `ParticleDecays:limitTau0 = on`, `tau0Max = 10 mm`: convención de CMS. K⁰_S, Λ, etc. los desintegra Geant4.
   - `Beams:allowVertexSpread = off`: PV = (0,0,0,0). El beamspot lo pone CMSSW.
   - `9000011:mayDecay = off`: el ẽ se desintegra solo según el LHE.

   La salida es HepMC2 (IO_GenEvent 2.06, `U GEV MM`, 10 cifras significativas) más dos tablas de verdad:
   una fila por ẽ y los jets de verdad anti-kT R = 0.5 (SlowJet/fjcore de Pythia), con pT > 20 GeV y |η| < 4.7,
   construidos con las partículas estables visibles sin los dos electrones del ẽ.
   Semillas de Pythia: 2200, 2300, 2400, 2500.
3. **Reflexión acausal**: `tools/lw_reflect_hepmc.py` (ver §3).
4. **Verificación**: `tools/hepmc_vertex_check.py` sobre los archivos HepMC (ver §2).
5. **Análisis de verdad**: `analysis/truth_analysis.py` (→ `analysis/summary_truth.csv`, `.txt`, `plots/`) y
   `analysis/lwrep_check.py` (lwRep = 0 frente a 1 a nivel partónico).

Todo se rehace con: `mg5/make_cards.py`, `mg5/run_mg5.sh`, `pythia/build.sh`, `./run_sample.sh M SEED` (Pythia, reflexión,
chequeo y gzip) y después los dos scripts de `analysis/`.

## 2. Cómo se verificó la propagación de los vértices

Pythia toma τ del LHE (VTIMUP = cτ propio en mm) y fija SV = PV + cτ·p/m en la **última copia** del ẽ, que es la que se
desintegra. La última copia importa porque el ẽ, al estar cargado, emite fotones QED (ẽ → ẽγ, estado 51), y además
hay copias por retroceso de ISR. Las hijas heredan el vértice: el e, el Z, los quarks, la cascada FSR, las copias de cuerda,
los hadrones primarios y las desintegraciones posteriores. La verificación tiene tres capas independientes:

- **En Pythia** (driver, `pythia_M*.log`, línea `LWSUMMARY`), sobre las 35 000 colisiones:
  - 0 descendientes en estado final producidos en el origen;
  - |SV − PV| = βγ·cτ con desviación relativa < 1.1·10⁻⁸;
  - 0 de 6.4·10⁶ hadrones primarios vienen de cuerdas que mezclen partones del ẽ con partones de fuera del ẽ.
    El Z → qq̄ es un singlete de color y la reconexión de color por defecto no lo mezcla. Por eso la asignación
    "pertenece a este SV" no es ambigua.
  - 2 partículas en M = 400 (ninguna en el resto) que no descienden del ẽ y tienen vértice no nulo sin madre hadrónica.
    Seguramente son radiación QED dentro de una desintegración. No afectan a la señal.
- **En el archivo HepMC** (`vertexcheck_M*.log`, `RESULT: PASS` para las 4 masas). En cada ẽ, la última copia se encuentra
  siguiendo el grafo HepMC. Sus descendientes estables se clasifican así:
  - exactamente en SV (|Δx| < 10⁻⁹ mm): unos 18 por ẽ (e, hadrones primarios de la cuerda);
  - más desplazados por una desintegración posterior (π⁰/η a escala de nm, τ, D, B…): unos 25 por ẽ;
  - **en el PV: 0** (M = 200: 718 278 en SV, 986 980 más allá, 0 en el PV).

  Cada paso aguas abajo es causal: el vértice está delante del vértice de producción de la madre en la dirección de su
  momento. La excepción son unos pocos pasos "hacia atrás" de **≤ 5 nm** en las copias partón → cuerda que hace Pythia.
  En esos casos todo el sistema de partones de un Z recibe un mismo desfase minúsculo respecto del SV
  (M = 200: 66 pasos en 20 000 eventos, máximo 4.9·10⁻⁶ mm; M = 300: 18; M = 400 y 500: 0).
  Son irrelevantes frente a los 20 μm de resolución y se cuentan aparte (`back_tiny`, umbral 10 nm).
  No se investigó su origen exacto dentro de Pythia.
- **Archivo acausal frente al causal**: en todos los ẽ se cumple SV′ = 2PV − SV con precisión 10⁻⁹ mm (`refl_ok` = todos).
  Las líneas `P` (momentos, estados, flujo de color) son byte a byte idénticas, ningún vértice fuera del árbol del ẽ se
  mueve, y κ_true > 0 en el 100 % de los ẽ causales y < 0 en el 100 % de los acausales.

## 3. Implementación de la acausalidad

Según Alvarez et al. (0908.2446, Ec. 1) y Grinstein–O'Connell–Wise (0805.2156), los productos de un ẽ salen de un vértice
desplazado **en sentido opuesto** a su momento total, con la misma ley exponencial de longitud βγcτ₀. A partir del evento
causal, `lw_reflect_hepmc.py` aplica a cada ẽ la traslación Δ = −2(SV − PV), es decir SV′ = PV − (SV − PV), al SV y a
**todos los vértices que cuelgan de él**: FSR del Z, fragmentación y desintegraciones de hadrones o τ. Así:

- Los descendientes siguen propagándose causalmente desde SV′. Por ejemplo, un B producido en SV′ vuela a lo largo de su
  momento. Solo el propagador del ẽ es acausal.
- Los momentos no cambian. Los archivos causal y acausal contienen **los mismos eventos** (números aleatorios comunes)
  y solo difieren en la posición de los vértices del árbol del ẽ.
- Por defecto también se refleja el tiempo (t′ = 2t_PV − t_SV; los productos "aparecen antes", con |Δt| ~ 0.1 ps).
  Con `--time keep` el tiempo no se toca.
- El script avisa si un vértice cuelga de los dos ẽ o recibe partículas de fuera del árbol (vértice "mixto").
  En todas las muestras hay 0 vértices mixtos.

Uso: `python3 tools/lw_reflect_hepmc.py in.hepmc[.gz] out.hepmc[.gz] [--time reflect|keep] [--pdg 9000011]`.
No necesita dependencias: el parser HepMC2 está en `tools/hepmc2io.py`. Sirve para cualquier HepMC2 de Pythia8
**antes** del smearing de vértice de CMSSW.

**Comparación con el "flip" del artículo** (simular causal y cambiar el signo de κ∥ de la señal). A nivel de verdad,
reflejar y hacer el flip son **idénticos por construcción**: κ′ = (−(SV − PV))·P = −κ, con el mismo P. En los gráficos,
`kappa_ref_plus_flip_maxabs = 0`. Solo pueden diferir después de la reconstrucción, es decir, en la fase 3:
- cortes geométricos relativos al beamspot o al PV reconstruido y el radio del beampipe en el algoritmo de vértices de [24];
- la asociación traza–PV: las trazas que salen "detrás" del PV pueden reabsorberse en el PV o dar un PV sesgado;
- el ajuste PV/SV con trazas cuyo parámetro de impacto tiene el signo opuesto;
- asimetrías de la eficiencia de reconstrucción de trazas desplazadas (seeding, hits en la primera capa).

## 4. Resultados de verdad

Archivo: `analysis/summary_truth.csv`. Las definiciones son las siguientes. βγ = |p|/M y βγ_T = p_T/M del ẽ (última copia).
L = |SV − PV| y L_T es su proyección transversal. La "selección tipo paper" exige dos electrones con p_T > 40/25 GeV y
|η| < 2.5, más ≥ 4 jets de verdad con p_T > 20 GeV y |η| < 2.5. WDVC significa L_T > 20 μm y |P_vis,T| > 20 GeV,
donde P_vis = e + 2 jets emparejados.

| M | ⟨βγ⟩ | ⟨βγ_T⟩ | ⟨L⟩ μm | ⟨L_T⟩ μm | mediana L_T | f(L_T > 20 μm) | ε sel. eventos | f(L_T > 20) tras sel. | f(WDVC) tras sel. |
|---|---|---|---|---|---|---|---|---|---|
| 200 | 2.05 | 0.733 | 55.6 | 20.0 | 10.7 | **31.5 %** | 51.8 % | 33.5 % | 27.4 % |
| 300 | 1.58 | 0.672 | 25.2 | 10.7 | 5.9 | 15.5 % | 66.7 % | 16.4 % | 13.5 % |
| 400 | 1.33 | 0.634 | 16.1 | 7.7 | 4.2 | 8.6 % | 71.4 % | 8.2 % | 6.4 % |
| 500 | 1.15 | 0.586 | 11.0 | 5.6 | 3.2 | 4.8 % | 71.3 % | 4.0 % | 2.9 % |

**Comparación con la estimación de juguete de la fase 1** (⟨βγ_T⟩ ≈ 0.40–0.55, ⟨L_T⟩ ≈ 11–14 μm, 15–22 % por encima de
20 μm para M = 200): la simulación completa da un boost transversal **mayor**, con ⟨βγ_T⟩ = 0.73 y ⟨L_T⟩ = 20 μm.
La fracción por encima de 20 μm es **31 %**, más o menos 1.5 veces la del juguete. El LHE solo, sin ISR, ya da
⟨βγ_T⟩ = 0.71, así que la diferencia viene de la cinemática partónica real (PDF + producción por γ*/Z), no de Pythia.
La distribución de L_T está muy concentrada en cero (mediana 10.7 μm < media) por la exponencial combinada con la
distribución de βγ_T. La señal sigue en el límite de la resolución de CMS.

### κ∥ = (SV − PV)·P_tot (verdad, M = 200; `plots/kappa_par_M*.png`)
- **Nivel partónico (a)**: e + q + q̄ del Z, con P_tot = p_ẽ exacto. κ∥ 3D tiene mediana 8.5 mm·GeV, media 36 mm·GeV,
  percentil 95 en 157 mm·GeV y percentil 99 en 435 mm·GeV. En cm·GeV todo se divide por 10 (mediana 0.85).
  La versión transversal, (SV − PV)_T·P_T, es mucho menor (mediana 1.3 mm·GeV).
  El 95 % de los ẽ cae en |κ∥| < 150 mm·GeV y el 62 % en < 15 mm·GeV.
- **Jets de verdad (b)**: e final + los dos jets líderes cuyo p_T viene en más de un 50 % del ẽ. El emparejamiento
  funciona en el 66 % de los ẽ. Mediana 6.9 mm·GeV, percentil 95 en 103 mm·GeV, y solo un 0.02 % de los ẽ causales da
  κ < 0. Si se toman sin emparejar los dos jets líderes del evento, el 8 % de los ẽ causales sale con κ < 0: la
  combinatoria ya "ensucia" el signo a nivel de verdad. Para los ẽ que pasan la WDVC: mediana 23 mm·GeV, percentil 90
  en 125 mm·GeV y 92 % dentro de ±150.
- **Rango de la Fig. 2 del artículo (−150…150, sin unidades)**: encaja con **mm·GeV y κ∥ 3D**, porque contiene alrededor
  del 92–95 % de la señal y deja las colas de vértices b y falsos en los extremos. En cm·GeV toda la señal ocuparía unos
  pocos bins centrales (|κ| < 15 cm·GeV casi siempre), y en μm·GeV la señal se saldría del rango. La versión transversal
  en mm·GeV también cabe, pero comprimida cerca de 0. Para la fase 3 conviene histogramar κ∥ 3D en mm·GeV y guardar
  también la versión transversal.

### Masas (`plots/masses_M*.png`)
- Partones: m_qq̄ tiene mediana 91.2 GeV y m_eqq̄ es exactamente M.
- Jets emparejados (M = 200): m_jj tiene mediana 88 GeV, con cola baja por FSR fuera del cono de 0.5. m_ejj tiene
  mediana 195 GeV.
- La ventana **80–160 GeV aplicada a m_jj** conserva el 72 % de los pares correctos (76 % para M ≥ 300). Aplicada a
  **m_ejj** conserva solo el 9 % para M = 200 y menos de un 1 % para M ≥ 300.
- Combinatoria tipo paper (cada electrón con cada par de jets buenos, unos 9 pares por electrón): solo el 11 % de los
  pares es el correcto. La ventana en m_jj sube la pureza al 14 % (M = 200) y hasta el 19 % (M = 500).
- **Conclusión: la ventana 80–160 GeV es casi seguro sobre m_jj** (el candidato Z). Sobre m_ejj eliminaría la señal de
  M = 200. Lo mejor sería añadir después un corte en m_ejj alrededor de M.

### lwRep = 0 frente a 1 (`analysis/lwrep_check.py`, `plots/lwrep_comparison_M200.png`, LHE, 20k + 20k eventos)
- σ(lwRep = 1)/σ(lwRep = 0) = **1.82**. Esto coincide con el factor 0.55 que se anotó en la fase 1, visto al revés.
- La cinemática cambia poco:
  - βγ media: 2.31 → 2.01 (KS D = 0.077);
  - βγ_T: 0.712 → 0.681 (D = 0.03);
  - ⟨L_T⟩ implícito: 19.3 → 18.4 μm;
  - |η(e)| es algo más central con lwRep = 1;
  - cos θ*, el ángulo de helicidad del e y el ángulo q del Z cambian con D ≤ 0.017.
- La elección lwRep = 0 casi no afecta al desplazamiento (alrededor de un 5 % en L_T). Sí afecta a la normalización.

## 5. Recomendaciones para la fase 3 (CMSSW_5_3_32)

1. **Formato: HepMC, no LHE.**
   - La geometría acausal no se puede codificar en un LHE: VTIMUP ≥ 0 es solo un tiempo de vida.
   - Hadronizar el LHE dentro de CMSSW_5_3 obliga a usar Pythia6 (Z2*), que ignora VTIMUP, o un Pythia8 de 2012
     (8.15x/8.17x) cuyo manejo de VTIMUP y de vértices en la interfaz HepMC de CMSSW no está verificado.
   - Recomendación: leer los `.hepmc` con la fuente `MCFileSource`
     (`cms.Source("MCFileSource", fileNames=cms.untracked.vstring('file:lw_M200_acausal.hepmc'))`).
     Hay que descomprimirlos antes: no está verificado que MCFileSource lea `.gz`.
   - La fuente produce el `HepMCProduct` con la etiqueta `source`. Hay que reapuntar `VtxSmeared.src`,
     `genParticles.src` y `g4SimHits.Generator.HepMCProductLabel` a `source`, o usar un `EDAlias` llamado `generator`.
   - Los archivos llevan `HepMC::Version 2.06.09` y `U GEV MM`, compatibles con el lector 2.06 de CMSSW_5_3
     (comprobar con un evento).
2. **Smearing de vértice.** `VtxSmeared` (p. ej. `Realistic8TeV2012Collision`) llama a `HepMCProduct::applyVtxGen`, que
   suma el mismo desplazamiento del beamspot a **todos** los vértices del evento. Es una traslación rígida, así que
   conserva los desplazamientos internos SV − PV y también la reflexión. Por eso hay que generar con PV = 0, como aquí, y
   **no** aplicar el smearing antes de reflejar. Hay que comprobar en el primer GEN que (SV − PV) del `HepMCProduct`
   después del smearing coincide con el del archivo de entrada.
3. **GEN-SIM.** `SimG4Core/Generators` (`Generator::HepMC2G4`) crea un `G4PrimaryVertex` por cada vértice HepMC que tiene
   hijas de estado 1. Las partículas de estado 2 que se desintegran dentro del corte de la beampipe (unos 2.9 cm) no se
   pasan a G4; se pasan sus hijas desde su propio vértice. Como los SV están a unas decenas de μm, los productos del ẽ
   entran a G4 desde SV o SV′. El ẽ (estado HepMC 62) no se propaga.
   - **Por verificar en la fase 3**: el tratamiento exacto de los estados ≠ 1, 2 en la versión 5_3_32 de `Generator.cc`;
     que no haya cortes sobre tiempos negativos (en caso de duda, usar `--time keep`); y el `genParticles` resultante.
   - Validación recomendada: procesar 100 eventos causales y 100 acausales hasta `g4SimHits` y comparar los
     `SimVertex` del e⁻ con los SV del HepMC.
4. Producir **los dos** GEN-SIM (causal y acausal) con las **mismas semillas** de CMSSW, para que las diferencias de
   reconstrucción entre la reflexión y el flip sean atribuibles solo a la geometría.
5. Para la selección:
   - aplicar la ventana 80–160 GeV a m_jj y estudiar un corte adicional en m_ejj;
   - definir κ∥ en 3D y en mm·GeV;
   - esperar una eficiencia de WDVC de verdad de alrededor del 27 % por ẽ tras la preselección (M = 200), que la
     resolución real reducirá todavía más.

## 6. Limitaciones / no verificado
- No se ha comprobado con CMSSW que la lectura de HepMC y el smearing conserven los vértices: lo de §5 sale del
  diseño conocido de esos módulos. Está pendiente para la fase 3.
- El tune es CUETP8M1 y no el Z2* de CMS 2012. Las PDF son nn23lo1 en MG5 y NNPDF2.3 LO en Pythia, no CTEQ6L1.
- Los jets de verdad usan la recombinación de SlowJet/fjcore en (y, φ, p_T), que es anti-kT estándar, y excluyen los dos
  electrones del ẽ. No hay fracción electromagnética ni identificación.
- `BR(ẽ → Ze) = 1`, como en el artículo. Las σ de esta carpeta son LO sin factor K y no son el resultado oficial de
  la fase 2.
- La partícula 9000011 se define en Pythia con M y cτ₀ (`9000011:all`). El SLHA del LHE solo aporta información:
  Pythia ignora las masas SM del SLHA por debajo de `SLHA:minMassSM`, así que usa su propio M_Z, que coincide con
  el del modelo en 91.1876 GeV.
