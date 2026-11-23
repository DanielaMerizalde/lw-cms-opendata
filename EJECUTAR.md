# Cómo ejecutar el proyecto desde cero con agentes

Esta guía arranca un proyecto **vacío** y lo lleva, con agentes, hasta el resultado final.
El flujo y las reglas están en `AGENTS.md`; los agentes, en `.claude/agents/`.

---

## 0. Requisitos (una sola vez)

| Herramienta | Para qué etapa | Comprobación |
|---|---|---|
| Claude Code (app de escritorio o `claude` en la terminal) | todas | `claude --version` |
| Wolfram Mathematica + FeynRules 2.3.49 (parcheado para Mathematica 15) | `teoria` | `wolframscript -code 1+1` |
| MadGraph5_aMC@NLO 3.8.1 con Pythia 8 | `generacion` | `mg5_aMC --version` |
| Docker Desktop con 6–8 GB de memoria e imagen `cmsopendata/cmssw_5_3_32` | `senal-cmssw`, `datos-cms`, `fondo-qcd` | `docker run --rm --platform linux/amd64 cmsopendata/cmssw_5_3_32 true` |
| Python 3 con numpy, matplotlib y uproot | `analisis`, `fondo-qcd`, `informe` | `python3 -c "import uproot"` |
| LaTeX (`pdflatex`) | `informe` | `pdflatex --version` |
| Red estable hacia `eospublic.cern.ch` (XRootD) | `datos-cms` | — |

---

## 1. Crear el proyecto vacío con la estructura de agentes

Desde una copia de este repositorio, se lleva a una carpeta nueva **solo la estructura**:

```bash
mkdir -p ~/proyectos/mi-reproduccion/docs ~/proyectos/mi-reproduccion/contratos/revisiones
```

```bash
cd ~/Downloads/lee-wick/lw-cms-opendata && cp -R .claude AGENTS.md CLAUDE.md EJECUTAR.md contratos ~/proyectos/mi-reproduccion/
```

Luego se copian a `docs/` los PDF del paper, de la tesis y de las referencias teóricas.

```bash
cd ~/proyectos/mi-reproduccion && git init -b main && git add -A && git commit -m "Estructura agéntica inicial"
```

---

## 2. Abrir Claude Code en esa carpeta

- **App de escritorio:** pestaña Code → elegir la carpeta `mi-reproduccion`.
- **Terminal:** `cd ~/proyectos/mi-reproduccion && claude`

Claude lee `CLAUDE.md` y con eso actúa como coordinador. Para comprobar que ve a los agentes, escribe `/agents`:
deben aparecer los 10.

---

## 3. El primer mensaje

> Eres el coordinador descrito en AGENTS.md. Quiero reproducir el paper que está en docs/ con CMS Open Data 2012.
> Crea contratos/PLAN.md y empieza por la etapa 1 con el agente lector-paper. Detente en el punto de control PC1.

A partir de aquí, el coordinador sigue el diagrama de `AGENTS.md`. Tu papel es responder en cada punto de control.

---

## 4. Qué pasa en cada etapa y qué te toca a ti

| Etapa | Mensaje para avanzar (después de aprobar la anterior) | Qué te muestra el coordinador | Lo que decides tú (✋) |
|---|---|---|---|
| 1. lector-paper | (el primer mensaje) | Los objetivos y las ambigüedades | **PC1:** ¿faltan objetivos?, ¿cómo resolver cada ambigüedad? |
| 2. teoria | "Aprobado PC1. Sigue con la etapa 2." | Tabla de cτ₀ nuestro/paper | **PC2:** si no coincide, cuál de las hipótesis aceptar (por ejemplo, m_e redondeada) |
| 3. generacion | "Aprobado PC2. Sigue con la etapa 3." | σ por variante y el costo estimado de la fase 4 | **PC3:** qué escenario usar (por ejemplo, solo Z o γ+Z) y cuántos eventos |
| 4a + 4b | "Aprobado PC3. Lanza 4a y 4b en paralelo." | Pruebas cortas: señal de 20 eventos, cutflow de 1 archivo | Si lanzar la producción completa (días de cómputo) |
| 5. fondo-qcd | "Sigue con la etapa 5." | R, fracción y forma del QCD | — (el verificador revisa) |
| 6. analisis | "Sigue con la etapa 6." | κ∥ frente al paper, con números | **PC4:** qué se concluye y qué falta |
| 8. informe | "Prepara el informe y la presentación." | Informe y presentación | **PC5:** qué sigue; si se comparte o se publica |

Cada decisión que tomes, el coordinador la anota en `contratos/decisiones.md`.

---

## 5. Las producciones largas (días)

Las etapas 4a, 4b y 5 lanzan scripts reanudables en segundo plano. Para que el `vigilante` los revise solo,
escribe en Claude Code:

> /loop 2h usa el agente vigilante para revisar la producción en phase3/analysis/qcd y relanzar los fallos transitorios

Para que la Mac no se duerma, las producciones se lanzan con `caffeinate -i -s`, que solo funciona con el cargador
conectado.

---

## 6. Retomar otro día

Abre Claude Code en la misma carpeta y escribe:

> Retoma el proyecto: lee contratos/PLAN.md y contratos/decisiones.md y dime en qué etapa estamos y qué falta.

El estado vive en los archivos (`PLAN.md`, `decisiones.md`, cada `ENTREGA.md` y cada `PROGRESS.md`), no en la
memoria de la conversación. Por eso se puede cerrar la sesión sin perder nada.

---

## 7. Pedir un agente a mano

Cualquier agente se puede invocar directamente, fuera del flujo:

> Usa el agente verificador para revisar generation/xsec/ENTREGA.md

> Usa el agente informe para hacer una presentación corta solo con las últimas actualizaciones

---

## 8. Cómo se ve el resultado

Al terminar, el repositorio tiene esta forma (es la de este repositorio):

```
contratos/        objetivos.json, decisiones.md, PLAN.md, revisiones/
model/            etapa 2  (teoria)
generation/       etapa 3  (generacion)
phase3/signal/    etapa 4a (senal-cmssw)
phase3/analysis/  etapas 4b, 5 y 6 (datos-cms, fondo-qcd, analisis)
docs/             etapa 8  (informe)
```
