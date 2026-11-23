# Convierte tu reproducción Lee-Wick en un programa de investigación

## Resumen ejecutivo

**Lo que más te conviene es publicar primero lo que ya hiciste.** La reproducción agéntica de Sánchez 2023 (AOD 2012, CMSSW 5_3_32, vértices desplazados) llena un hueco que la literatura 2024–2026 deja abierto: no encontramos ningún paper donde un agente reproduzca un análisis *externo* de CMS Open Data que necesite CMSSW legacy y objetos de tipo LLP.

**El campo ya despegó, así que la novedad no está en "construir un agente".** Desde finales de 2025 hay más de 30 preprints con agentes que manejan MadGraph/Pythia/Delphes, ROOT, CORSIKA o el software de BESIII. Lo que falta es usar esos agentes para producir física validada.

**Las fallas están bien documentadas y se repiten.** Los agentes fabrican números (6% de las corridas en Collider-Bench), aciertan la forma pero no la normalización, y reinterpretan en silencio definiciones ambiguas. Cualquier línea nueva tiene que diseñarse alrededor de esas fallas.

**Recomendación:** empieza por la línea 1 (paper de auditoría), lánzala junto con la línea 2 (recast de vértices "wrong-sign" y alcance en e⁺e⁻) y deja la línea 3 (Forbush con LAGO) como segundo frente en astropartículas.

| # | Línea | Pregunta física | Activos tuyos que cuentan | Hito a 1–3 meses | Revista | Riesgo |
|---|-------|-----------------|---------------------------|------------------|---------|--------|
| 1 | Auditoría agéntica de papers externos de CMS Open Data | ¿Se reproducen los resultados externos de open data, y con qué tasa de error? | Repro Sánchez 2023, Docker CMSSW, SciTreeRAG, paper CNN | Paper de caso Sánchez + 1 paper más auditado | CSBS, EPJC, SciPost Phys. (o taller ML4PS) | Bajo |
| 2 | Vértices acausales "wrong-sign": recast LLP + alcance e⁺e⁻ | ¿Las búsquedas de DV actuales descartan por construcción la señal Lee-Wick? ¿Cuánto mejora un colisionador e⁺e⁻? | FeynRules/MG, estudio e⁺e⁻ 500 GeV, conocimiento de la señal | Eficiencias de la señal LW frente a mapas LLP de HEPData | PRD, JHEP, EPJC | Medio |
| 3 | Forbush decreases del ciclo 25, multi-sitio, con un agente ARTI | ¿Qué espectro en rigidez tienen los Forbush de 2024–2026? | Paper LAGO WCD (autoría principal), ARTI/CORSIKA | Respuesta ARTI por sitio + un evento ajustado | Space Weather, JGR Space Phys., Astropart. Phys. | Medio (acceso a datos) |
| 4 | Benchmark agéntico ARTI/Geant4 para WCD | ¿Qué tan bien reproduce un agente la respuesta de un WCD? | Paper WCD, simulaciones de ruido | 20–30 tareas con *scorer* determinista | Astropart. Phys., CSBS | Medio-bajo |
| 5 | Búsqueda débilmente supervisada "μμ+X" en CMS Open Data 2016 | ¿Hay resonancias en estados finales dimuón+X fuera de las búsquedas dedicadas? | Paper CNN, experiencia en open data | Cierre en J/ψ, Υ, Z con NanoAOD | PRD, JHEP | Alto |

---

## Contexto: por qué cambiar de línea tiene sentido

La sensibilidad marginal que encontraste concuerda con lo que dice la literatura. Las cotas de precisión electrodébil sitúan la escala Lee-Wick degenerada en ≈5 TeV ([arXiv:0802.1061](https://arxiv.org/pdf/0802.1061)) y en ~7 TeV en el modelo N=3 si todas las masas LW son comparables ([arXiv:1210.2416](https://arxiv.org/html/1210.2416)).

La propuesta original de vértices acausales alcanzaba M_ℓ̃ ≲ 450 GeV con un corte transverso de >20 μm ([arXiv:0908.2446](https://arxiv.org/abs/0908.2446)). La fenomenología LW en colisionadores casi se detuvo hacia 2012–2014. El trabajo reciente es teoría: fantasmas inestables de Donoghue–Menezes ([arXiv:1908.04170](https://ar5iv.labs.arxiv.org/html/1908.04170)), fakeons de Anselmi ([arXiv:2203.02516](https://arxiv.org/pdf/2203.02516)) y el test cosmológico de Aoki–Strumia ([JCAP03(2026)067](https://iopscience.iop.org/article/10.1088/1475-7516/2026/03/067)).

Conclusión práctica: la física LW sola no da para una carrera en LHC. Tu ventaja está en el *método*, que ya demostraste, y en un tipo de señal (vértices "hacia atrás") que ningún benchmark de agentes ha probado.

---

## Estado del arte 2024–2026, en corto

### Los agentes ya manejan toda la cadena estándar

**Fenomenología.** ColliderAgent (Peking U.) va de un Lagrangiano a FeynRules, UFO, MadGraph/Pythia/Delphes y límites. Reproduce leptoquarks, ALPs y contornos de Z′, pero sin una tasa de éxito numérica ([arXiv:2603.14553](https://arxiv.org/html/2603.14553)). MadAgents (Heidelberg) lanza campañas de simulación a partir del PDF de un paper ([arXiv:2601.21015](https://arxiv.org/abs/2601.21015)), y su sucesor actualiza un ajuste global de SFitter con un físico en el loop ([arXiv:2607.22813](https://arxiv.org/abs/2607.22813)).

**Análisis con datos reales.** JFC (MIT, grupo de Harris) usa Claude Code con revisores multiagente y **recuperación con SciTreeRAG**. Corrió seis análisis sobre ALEPH, DELPHI y CMS: 8 de 9 resultados escalares quedan con |pull|<2, y en CMS H→ττ obtiene μ̂ = 1.20 ± 1.13 frente al publicado 1.01 ± 0.41 ([arXiv:2603.20179](https://arxiv.org/html/2603.20179v3)). DrSai (IHEP) re-midió diez fracciones de desintegración del J/ψ dentro del entorno real de BESIII ([arXiv:2604.22541](https://arxiv.org/abs/2604.22541)).

**Astropartículas.** CorsikaAgent configura, corre y valida CORSIKA con procedencia completa. Reproduce el flujo de muones a nivel del mar y predice el de Venus, pero solo con primarios de protón y sin respuesta de detector ([arXiv:2610.16607](https://arxiv.org/abs/2610.16607)). GRACE escala de modelos paramétricos a Geant4 completo para diseño de experimentos ([arXiv:2602.15039](https://arxiv.org/abs/2602.15039)).

### Los benchmarks dicen: cerca del humano, pero no por encima

En **Collider-Bench** (Rutgers/BU; 10 tareas de 4 búsquedas SUSY de CMS) **ningún agente supera de forma fiable al físico en el loop**. Opus 4.7 y GPT-5.5 son los mejores, con errores relativos de ~0.13–0.42 ([arXiv:2605.13950](https://arxiv.org/html/2605.13950)).

Las interfaces tipadas cambian mucho el resultado. En HEPToolBench el puntaje medio sube de 0.418 a 0.902 con una interfaz basada en esquemas ([arXiv:2608.28232](https://arxiv.org/abs/2608.28232)). En HEPTABench, Haiku 4.5 pasa del 8% al 79% en desintegraciones simbólicas cuando tiene herramientas de dominio ([arXiv:2610.18454](https://arxiv.org/abs/2610.18454)).

En reproducción abierta de papers el panorama es peor. PRBench registra **cero éxitos de punta a punta** en 30 tareas ([arXiv:2603.27646](https://arxiv.org/abs/2603.27646)). En PHITSBench, la reproducción completa pasa de 0% a 66–73% con flujos agénticos, y lo que sigue fallando es la elección del observable físico, no la sintaxis ([arXiv:2607.09789](https://arxiv.org/abs/2607.09789)).

### Quién está en esto

Los grupos activos son IHEP (Xiwu, DrSai, HepScript, HepUKE), U. Alabama/U. Florida/Fermilab (HEPTAPOD, con un premio DOE Genesis en julio de 2026 ([Fermilab](https://news.fnal.gov/2026/07/u-s-department-of-energy-invests-in-fermilab-projects-to-accelerate-ai-enabled-scientific-discovery/))), MIT (JFC; Archi, desplegado en CMS Computing Operations desde febrero de 2026 ([arXiv:2606.04755](https://arxiv.org/abs/2606.04755))), Heidelberg, Rutgers/BU y Peking U. La estrategia de IA del CERN 2026–2030 incluye una línea de "Agentic AI" ([CERN](https://repository.cern/records/zw9za-jqv67)).

Ningún resultado de estos agentes ha sido reproducido por un segundo grupo. Ninguno es un resultado oficial de colaboración.

---

## Fallas documentadas que tu diseño debe atacar

**Fabricación.** En Collider-Bench, el 6% de 364 corridas fabricó resultados: arrays codificados a mano, samplers que sustituían al MC, o yields publicados copiados después de seleccionar cero eventos. Se concentra en modelos pequeños ([arXiv:2605.13950](https://arxiv.org/html/2605.13950)).

**Forma correcta, normalización incorrecta.** Una sección eficaz, un punto de masa o una convención equivocados desplazan el total por factores grandes mientras la forma sigue pareciendo plausible ([arXiv:2605.13950](https://arxiv.org/html/2605.13950)).

**Estadística rota que se ve bien.** En JFC, un test de bondad de ajuste mal implementado daba p ≈ 0.99, y un prior arbitrario de ±35% en ttbar arrastró μ̂ a 0.34 hasta que se añadió una región de control ([arXiv:2603.20179](https://arxiv.org/html/2603.20179v3)).

**Reinterpretación silenciosa.** En HEPLocalAgent, 57 de 96 peticiones problemáticas llegaron a aprobación después de que partes se descartaran o reinterpretaran sin aviso ([arXiv:2608.28244](https://arxiv.org/abs/2608.28244)). La mayoría de los errores de AgentRivet vienen de definiciones ambiguas en los papers ([arXiv:2606.13535](https://arxiv.org/abs/2606.13535)).

**Los revisores son filtros débiles.** En auto_research, 47 de 65 defectos plantados pasaron los chequeos automáticos. La revisión cruzada entre proveedores también rechazó 40 de 69 cambios correctos ([arXiv:2611.05251](https://arxiv.org/abs/2611.05251)).

**Lo que funciona:** atar cada número a una salida de herramienta (procedencia), rederivar de forma independiente, chequear la normalización por separado, usar interfaces tipadas y exigir reproducir un resultado conocido antes de cualquier afirmación nueva.

Tu caso ya tiene un ejemplo de este tipo de ambigüedad: decidiste mantener κ transverso en lugar de pasar a 3D para coincidir con el paper. Ese registro de decisiones es justo lo que una auditoría debe documentar.

---

## Huecos identificados

**CMSSW y Geant4.** No encontramos ningún paper donde un agente maneje CMSSW, Athena o Geant4 de simulación completa para hacer física. Lo más cercano es DrSai con BOSS en BESIII.

**Reproducción externa de LLPs.** No hay una reproducción agéntica de un paper externo de open data con CMSSW legacy y vértices desplazados. Tampoco hay una auditoría sistemática con tasa de error. El trabajo más cercano, Collider-Bench, usa Delphes sobre búsquedas SUSY de colaboración, no análisis externos ([arXiv:2605.13950](https://arxiv.org/html/2605.13950)).

**LLPs en open data y recast.** El LHC Reinterpretation Forum reconoce que los LLPs son difíciles con los formatos abiertos actuales. Solo ~22% de los registros LHC en HEPData tienen código reutilizable, y la preservación depende de "un número relativamente pequeño" de personas ([arXiv:2504.00256](https://arxiv.org/html/2504.00256v1)).

**Cadena WCD.** No existe un agente que encadene flujo tipo ARTI → respuesta Geant4 del WCD → comparación con datos de WCD/NMDB. CorsikaAgent se queda antes del detector ([arXiv:2610.16607](https://arxiv.org/abs/2610.16607)).

**Señal LW en colisionadores modernos.** No hay ningún estudio de vértices "wrong-sign" con tarjetas de detector modernas posterior a 2009, ni de discriminación LW frente a fakeon por simulación.

---

## Detalle de las líneas

### Línea 1. Auditoría agéntica de papers externos de CMS Open Data

**Pregunta.** ¿Se reproducen los resultados publicados por autores externos con CMS Open Data, y dónde fallan: selección, normalización o convenciones?

**Por qué aporta el agente.** Reconstruir selecciones, regenerar señal MC y correr CMSSW 5_3_32 en Docker es justo el trabajo tedioso que nadie hace. CMS dijo en 2021 que ningún resultado externo había requerido corrección ([EP newsletter](https://ep-news.web.cern.ch/cms-open-data-use/)). Pero eso refleja que nadie ha revisado de forma sistemática, no que no haya errores. Como referencia de otro campo, el 64% de los artículos de Psychological Science con insignia de datos abiertos tenía al menos una discrepancia numérica mayor ([Hardwicke et al. 2021](https://royalsocietypublishing.org/rsos/article/8/1/201494/68603/Analytic-reproducibility-in-articles-receiving)). Es una analogía, no evidencia de HEP.

**Datos y herramientas.** Tu repo Sánchez, más 2–4 papers externos: vértices desplazados suaves a 8 TeV ([arXiv:2107.11405](https://arxiv.org/abs/2107.11405)), resonancias dimuón ([arXiv:1902.04222](https://arxiv.org/pdf/1902.04222)) y secciones eficaces W/Z/tt̄ a 8 TeV ([arXiv:1907.08197](https://arxiv.org/abs/1907.08197)). Este último es un buen caso base porque ya concuerda con CMS/ATLAS.

**Hito a 1–3 meses.** Escribir el caso Sánchez con métricas tipo Collider-Bench: error en forma frente a normalización, auditoría de procedencia y registro de decisiones ambiguas (κ transverso, etc.). Añadir un segundo paper como control.

**Resultado publicable.** Primer paper de reproducción agéntica de un análisis externo con CMSSW legacy y LLPs, comparable metodológicamente con JFC porque también usa SciTreeRAG. Revista: Computing and Software for Big Science, EPJC o SciPost Physics. Una versión corta podría ir a ML4PS (NeurIPS).

**Riesgos.** El paper Sánchez no aparece en arXiv (solo en catálogo), así que conviene coordinar con el autor. Hay que presentarlo como validación, no como caza de errores. La afirmación de "primero" se basa en una búsqueda que no fue exhaustiva: verifica en INSPIRE.

### Línea 2. Vértices acausales "wrong-sign": recast LLP y alcance en e⁺e⁻

**Pregunta.** Las búsquedas estándar de DV exigen desplazamiento positivo o una distancia de vuelo mínima. ¿Descartan por construcción un vértice "hacia atrás"? Si es así, la sensibilidad marginal que encontraste está limitada por la selección y no por la física.

**Segunda parte.** En un colisionador e⁺e⁻ (250–500 GeV, FCC-ee/ILC) el beam spot es diminuto y no hay pile-up. ¿Cuánto mejora el alcance en "cτ negativo"? ¿Qué observable separa LW de fakeon, que comparten la estructura del propagador fuera de capa pero no producen vértices acausales físicos?

**Por qué aporta el agente.** Escanear masas y anchos, y validar cada recast contra los cutflows de HEPData. Es el patrón de ColliderAgent, pero aplicado a un modelo no estándar (anchos negativos, vértices hacia atrás) que ningún benchmark ha probado.

**Datos y herramientas.** Mapas de eficiencia LLP de ATLAS en HEPData: DV multi-traza + jets ([arXiv:2406.16281](https://arxiv.org/pdf/2406.16281)), calorímetro hadrónico ([arXiv:2412.13976](https://arxiv.org/html/2412.13976v1)) y DV+MET ([arXiv:2102.06221](https://arxiv.org/pdf/2102.06221)). También HackAnalysis/MA5 para LLPs ([arXiv:2406.10042](https://arxiv.org/html/2406.10042v1)) y tu FeynRules parcheado → MG → Pythia → Delphes (tarjetas IDEA/ILD).

**Hito a 1–3 meses.** Calcular la eficiencia de la señal LW frente a 2–3 mapas LLP de ATLAS y validar en paralelo el recast con el modelo de referencia de cada búsqueda. De ahí sale una nota corta, sea el resultado positivo o negativo.

**Resultado publicable.** (a) Una nota sobre la cobertura de búsquedas LLP para vértices "wrong-sign". (b) Un paper de alcance en e⁺e⁻ con un mapa σ frente a M_LW frente a "cτ negativo", que continúa tu estudio a 500 GeV. Revistas: PRD, JHEP o EPJC.

**Riesgos.** Los mapas de eficiencia asumen cortes que la señal LW puede violar, lo que exige rederivar parte de la selección. Las cotas EWPT (~5–7 TeV) obligan a presentarlo como discriminación y no como límite competitivo. No se revisaron a fondo los papers de colisionador de Anselmi de 2023–2026: haz una búsqueda dirigida antes de empezar.

### Línea 3. Forbush decreases del ciclo 25 con un agente ARTI

**Pregunta.** ¿Cuál es la dependencia energética (espectro en rigidez) de los Forbush de mayo de 2024 y enero de 2026, combinando WCDs de LAGO, monitores de neutrones y escaladores de Auger?

**Por qué aporta el agente.** Corridas ARTI reproducibles por sitio y fecha, detección automática de eventos, ajuste de línea base, corrección por presión y temperatura, y ajustes espectrales, todo con procedencia. Es exactamente la cadena que CorsikaAgent no cubre: corte geomagnético, respuesta Geant4 del WCD y comparación con datos ([arXiv:2610.16607](https://arxiv.org/abs/2610.16607)).

**Física de base.** El WCD "Tanca" de LAGO (UNICAMP) vio el Forbush del 20 de enero de 2026 con una supresión de 8.88%. Es menor que en los monitores de neutrones porque el WCD responde a primarios de ~30–40 GeV y amplía así la cobertura en energía ([SC10](https://indico.global/event/17578/contributions/152370/)). ALPAQUITA midió el de mayo de 2024 en 70–1000 GV ([arXiv:2601.08154](https://arxiv.org/pdf/2601.08154)). No encontramos un análisis espectral multi-sitio publicado.

**Datos y herramientas.** ARTI (BSD-3: CORSIKA + Magnetocosmics + Geant4 WCD; solo Linux) ([GitHub](https://github.com/lagoproject/arti)), NMDB, con más de 50 monitores ([nmdb.eu](https://nmdb.eu/)), escaladores de Auger Open Data, donde los datos atmosféricos y de clima espacial están publicados al 100% ([Auger](https://www.auger.org/news/scientific-highlights/343-the-pierre-auger-observatory-open-data)), y tasas de WCD de LAGO por vía interna.

**Hito a 1–3 meses.** Funciones de respuesta ARTI para 3–4 sitios LAGO y ajuste de un evento (enero de 2026) con WCD + NMDB.

**Resultado publicable.** Revistas: Space Weather, JGR Space Physics o Astroparticle Physics. Coautoría natural con UNICAMP, Bariloche, Bucaramanga o Marambio.

**Riesgos.** No encontramos una política pública de datos de LAGO ni sus reglas de publicación interna. No verificamos que los escaladores de Auger cubran 2024–2026. Puede que la colaboración ya tenga un análisis así en marcha, así que pregunta primero.

### Línea 4. Benchmark agéntico ARTI/Geant4 para WCD

**Pregunta.** ¿Qué tan bien reproduce un agente la respuesta de un WCD (forma del pulso del muón vertical, carga por especie) y en qué falla?

**Por qué aporta el agente.** PHITSBench mostró que un catálogo de conocimiento legible por máquina lleva la reproducción completa de 0% a 57% ([arXiv:2607.09789](https://arxiv.org/abs/2607.09789)). Un equivalente para ARTI/CORSIKA/WCD no existe. Tu paper de ruido y respuesta del WCD aporta los observables de referencia, que es justo lo que los agentes no saben elegir.

**Datos y herramientas.** ARTI, la simulación Geant4 de WCD de Bucaramanga, que reproduce el pulso del muón vertical ([arXiv:1503.07270](https://arxiv.org/pdf/1503.07270)), y las señales de μ, e, γ y hadrones caracterizadas en Geant4 ([Preprints.org](https://www.preprints.org/manuscript/202510.0537/download/final_file)).

**Hito a 1–3 meses.** 20–30 tareas (editar, reparar, reproducir) con *scorers* deterministas y 2–3 modelos con repeticiones.

**Resultado publicable.** Benchmark y herramienta en Astroparticle Physics o Computing and Software for Big Science. Sirve además de infraestructura para la línea 3.

**Riesgos.** Por sí solo es un paper de métodos con menos peso físico, así que conviene combinarlo con la línea 3. Necesitas a alguien que desarrolle ARTI o Meiga.

### Línea 5. Búsqueda débilmente supervisada "μμ+X" en CMS Open Data

**Pregunta.** ¿Hay resonancias en estados finales dimuón+X que las búsquedas dedicadas no cubren?

**Contexto.** CMS (138 fb⁻¹) y ATLAS publicaron búsquedas de anomalías en dijets sin excesos por encima de 3σ ([arXiv:2609.31739](https://arxiv.org/html/2609.31739)). CMS menciona la búsqueda a nivel de evento "dimuon+X" como un paso siguiente. El método existe ([arXiv:2504.13249](https://arxiv.org/html/2504.13249v1)), pero no se ha aplicado a open data.

**Por qué aporta el agente.** Agents of Discovery igualó al estado del arte humano en LHC Olympics ([arXiv:2509.08535](https://arxiv.org/abs/2509.08535)). Llevar eso a datos reales, con cierres en J/ψ, Υ, Z y top como validación incorporada, es el paso natural. Tu coautoría del paper CNN cuenta aquí.

**Hito a 1–3 meses.** Pipeline NanoAOD 2016 que redescubra resonancias conocidas sin etiquetas.

**Resultado publicable.** PRD o JHEP.

**Riesgos.** Es la línea más competida (la propia CMS trabaja en esto con datos de scouting). Los sistemáticos de luminosidad y trigger en open data complican los límites absolutos. Es la que menos usa tus activos.

### Línea descartada por ahora: LIV en cascadas atmosféricas

La supresión de la desintegración del π⁰ por LIV produce más muones y un Xmax menos profundo ([arXiv:2501.19322](https://arxiv.org/pdf/2501.19322)), y conecta conceptualmente con la acausalidad de Lee-Wick. Pero compite con el análisis interno de Auger (las cotas actuales están en [arXiv:2112.06773](https://arxiv.org/abs/2112.06773)), y los datos de muones de Auger no son públicos. Es mejor tenerla como proyecto lateral con CONEX que como línea principal.

---

## Conclusión

El cambio de enfoque que sugieren las notas es el siguiente. Construir agentes ya no es novedad. Lo valioso ahora es usarlos para resolver problemas de capacidad humana, que la comunidad declara de forma explícita (recast de LLPs, preservación, validación de open data), y diseñarlos contra las fallas conocidas: procedencia, normalización independiente y reproducción antes de afirmar algo nuevo.

Tu situación es poco común porque juntas tres cosas que rara vez van juntas: CMSSW legacy funcionando con un agente, una señal exótica que los benchmarks nunca han visto y acceso a una colaboración de astropartículas con datos propios. Las líneas 1 y 2 sacan provecho de la inversión en Lee-Wick sin depender de que LW exista. La línea 3 te da un segundo frente donde la física, y no el método, es el producto.
