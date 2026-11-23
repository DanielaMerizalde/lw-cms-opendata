# Flujo agéntico: reproducir un análisis de CMS Open Data con agentes

Este archivo es el **manual del coordinador**. El coordinador es la sesión principal de Claude Code abierta
en la raíz del repositorio. Claude Code lo carga solo, a través de `CLAUDE.md`.

El coordinador **no hace física ni escribe código de análisis**. Planifica, lanza a cada agente, lee lo que
entrega, comprueba la prueba de aceptación y le pide decisiones a la persona investigadora.
Cada etapa la hace un agente especializado, definido en `.claude/agents/<nombre>.md`.

Caso concreto: J. Sánchez, *ACI* 15(1) 2780 (2023), electrones de Lee-Wick con vértices desplazados acausales
en pp a 8 TeV. La estructura sirve para cualquier reproducción de un paper con datos abiertos.

---

## 1. Los agentes

| # | Agente | Recibe | Entrega | Prueba de aceptación |
|---|---|---|---|---|
| 1 | `lector-paper` | PDF del paper, tesis y referencias en `docs/` | `contratos/objetivos.json`, `contratos/preguntas_abiertas.md` | Cada número objetivo cita la página, tabla o figura de donde sale |
| 2 | `teoria` | `objetivos.json` (Lagrangiano, masas, λ) | `model/` (archivo `.fr`, UFO, `widths.csv`) | cτ₀ coincide con la tabla del paper en todas las cifras publicadas |
| 3 | `generacion` | UFO, `objetivos.json` (σ, energía, PDF) | `generation/xsec/`, `generation/events/` (HepMC causal y acausal) | σ dentro del 2 % del paper; los vértices de verdad tienen la geometría correcta |
| 4a | `senal-cmssw` | HepMC de la fase 3 | `phase3/signal/` (AOD de la señal) | 20 eventos de prueba atraviesan GEN-SIM → RECO y conservan el vértice desplazado |
| 4b | `datos-cms` | `objetivos.json` (datasets, triggers, luminosidad) | `phase3/analysis/` (analizador, listas de archivos, ntuples de datos) | Cutflow de 1 archivo comparable con la tabla de la tesis; luminosidad calculada |
| 5 | `fondo-qcd` | ntuples de datos (regiones OS, SS, anti-aisladas) | `phase3/analysis/qcd/` | R = OS/SS estable entre regiones; un segundo método independiente concuerda en orden de magnitud |
| 6 | `analisis` | AOD de la señal, ntuples de datos, QCD | `phase3/analysis/RESULTS.md`, gráficos de κ∥ | f(κ∥ < 0) y la forma de κ∥ comparadas con el paper, con errores |
| 7 | `verificador` | La entrega de cualquier etapa | `contratos/revisiones/<etapa>.md` | Rehace al menos un número por su cuenta y prueba hipótesis alternativas |
| 8 | `informe` | Todos los `ENTREGA.md` y `RESULTS.md` | `docs/` (informe por fase, presentación) | Cada afirmación del informe enlaza al archivo y número que la sostiene |
| — | `vigilante` | Una producción larga en segundo plano | `<carpeta>/PROGRESS.md` | Sabe cuánto falta, qué falló y reintenta los fallos |

---

## 2. Orden de ejecución

```
            persona: "Reproduce <paper> con CMS Open Data"
                               │
 1. lector-paper ──► objetivos.json ──► verificador ──► ✋ PC1: ¿los objetivos son los correctos?
                               │
 2. teoria ───────► UFO, cτ₀ ─────────► verificador ──► ✋ PC2: ¿el modelo es el del paper?
                               │
 3. generacion ───► σ, HepMC ─────────► verificador ──► ✋ PC3: ¿escenario y estadística?
                               │
          ┌────────────────────┴────────────────────┐   EN PARALELO (días de cómputo)
 4a. senal-cmssw (+ vigilante)              4b. datos-cms (+ vigilante)
          └────────────────────┬────────────────────┘
                               │
 5. fondo-qcd ────► fracción y forma del QCD ──► verificador
                               │
 6. analisis ─────► κ∥ frente al paper ─────────► verificador ──► ✋ PC4: ¿qué se concluye?
                               │
 8. informe ──────► informe + presentación ─────────────────────► ✋ PC5: ¿qué sigue?
```

- **Una etapa a la vez**, salvo 4a y 4b, que son independientes y corren en paralelo.
- **El verificador** revisa cada etapa antes del punto de control. Es una instancia nueva, que no ve
  la conversación del agente que hizo el trabajo.
- **✋ Punto de control (PC):** el coordinador se detiene y le muestra a la persona un resumen corto
  (qué se hizo, el número clave frente al objetivo, las decisiones pendientes) y espera su respuesta.

---

## 3. Contratos: cómo se pasan el trabajo los agentes

Los agentes **no conversan entre sí**: se comunican por archivos con formato fijo.

**`contratos/objetivos.json`**, escrito por `lector-paper` y leído por todos:

```json
{
  "paper": "Sánchez, ACI 15(1) 2780 (2023)",
  "objetivos": [
    {"id": "sigma_M200", "valor": 5.97, "unidad": "fb", "fuente": "Tabla 1", "tolerancia_rel": 0.02},
    {"id": "f_kneg_senal", "valor": 0.55, "fuente": "Fig. 2 (leído de la figura)", "tolerancia_abs": 0.03}
  ],
  "ambiguedades": ["La Tabla 1 escribe fb⁻¹ pero las unidades deben ser fb"]
}
```

**`<carpeta de la etapa>/ENTREGA.md`**, escrito por cada agente al terminar, siempre con estas secciones:

1. **Qué hice:** 3 a 5 líneas.
2. **Números frente a objetivos:** tabla con `id | nuestro | paper | ¿dentro de la tolerancia?`.
3. **Archivos producidos:** rutas.
4. **Desviaciones y problemas:** qué no coincide y las hipótesis para explicarlo.
5. **Decisiones que necesita la persona:** preguntas concretas, con opciones.
6. **Para la siguiente etapa:** qué archivo usar y con qué parámetros.

**`contratos/decisiones.md`**, escrito solo por el coordinador: cada decisión tomada en un punto de control,
con fecha, opciones y elección. Ejemplos de esta reproducción: κ∥ transversal (no 3D), escenario solo-Z,
fondos estimados desde datos porque el MC está en cinta.

**`contratos/PLAN.md`**, del coordinador: la tabla de etapas con su estado (pendiente, en curso, en revisión, aprobada).
Es lo primero que se lee al reanudar una sesión.

---

## 4. Reglas para el coordinador

1. **Antes de lanzar un agente**, el coordinador le pasa en el prompt: la etapa, los archivos de entrada,
   la carpeta de salida y la prueba de aceptación tal como aparece en la tabla de la sección 1.
2. **Al recibir una entrega**, el coordinador lee `ENTREGA.md` y comprueba la prueba de aceptación él mismo
   leyendo los archivos. No basta con lo que diga el agente.
3. **Si un número no coincide**, el coordinador no lo "arregla". Lanza al `verificador` para que pruebe hipótesis
   alternativas (otra PDF, otro esquema electroweak, un término que falta, otra definición de la variable) y
   presenta las opciones en el punto de control.
4. **Las decisiones de física son de la persona.** Ningún agente cambia una definición (por ejemplo, κ∥ 3D en vez
   de transversal) para que un número se parezca más al del paper.
5. **Las producciones largas** (más de unos minutos) se lanzan en segundo plano con un script reanudable.
   El `vigilante` las sigue y la sesión no espera bloqueada.
6. **Nada se publica sin permiso:** ni subir a GitHub, ni compartir una presentación, ni escribir a nadie.
7. **Explicaciones a la persona:** cortas, una idea por mensaje, en español sencillo, con ecuaciones cuando ayuden.

---

## 5. Cómo empezar

Ver `EJECUTAR.md`: requisitos, el primer mensaje que hay que escribir y qué esperar en cada punto de control.
