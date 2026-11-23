# Modelo teórico (fase 1): electrón de Lee-Wick

Reproducción de J. Sánchez, *ACI Av. Cienc. Ing.* **15**(1) 2780 (2023), Ec. (1), tomada de
Alvarez, Da Rold, Schat, Szynkman, JHEP 10 (2009) 023 [arXiv:0908.2446].
Señal: pp → ẽ⁺ẽ⁻ → e⁺Z e⁻Z a 8 TeV. **Aquí solo están el modelo, el UFO y la validación del ancho / cτ₀.**
No se generan eventos ni se calculan secciones eficaces.

## Contenido

| Archivo | Qué es |
|---|---|
| `LWElectron.fr` | Extensión de `SM.fr` (FeynRules) con el electrón LW `elw` |
| `sanity_sm.wls` | Prueba previa: FeynRules parcheado + SM.fr encuentra el vértice e e A |
| `run_fr.wls` | Carga SM.fr + LWElectron.fr, chequeos (hermiticidad, cinético, masa), imprime vértices, `ComputeWidths`, `WriteUFO` |
| `LWElectron_UFO/` | UFO generado (SM completo en gauge de Feynman + `elw`) |
| `mg5_widths.py` | Importa el UFO en MG5 3.8.1 y corre `compute_widths elw-` para M = 200–500 GeV y dos valores de m_e |
| `mg5/` | Tarjetas de parámetros de entrada/salida y scripts `.mg5` generados por `mg5_widths.py` |
| `widths.csv` | Tabla final: Γ_FR, Γ_MG5, cτ₀ y razón con λ de la Tabla 1 del artículo |
| `logs/` | `sanity_sm.log`, `run_fr.log`, `LWElectron_UFO.log`, `mg5_*.log`, `widths_fr.csv`, `widths_mg5.csv` |

## Partícula y parámetros nuevos

- `elw` (ẽ): fermión de Dirac, Q = −1, número leptónico +1, PDG **9000011**, nombres MG `elw-` / `elw+`.
  Masa `MLW` (bloque MASS, defecto 200 GeV), ancho `WLW` (bloque DECAY, defecto 7.28775e-12 GeV = valor calculado para M = 200, MeLW = 5e-4).
- Bloque `LWINPUTS`:
  - `MeLW` (1): m_e que entra en el acoplamiento de mezcla m_e/M. **Defecto 5.0e-4 GeV** (reproduce λ de la Tabla 1 del artículo a 1e-6); 5.11e-4 es el valor PDG. Es independiente de `Me` del SM.
  - `etaLW` (2): signo LW de los acoplamientos ẽẽγ y ẽẽZ relativos al electrón del SM. Defecto −1 (Ec. 1 literal).
  - `lwRep` (3): acoplamiento de ẽ_R al Z. **0 (defecto) = Ec. 1 literal** (ẽ_R con g_Z^{eR}); **1 = socio vectorial del doblete** (ẽ_R con g_Z^{eL}, como en Alvarez et al. Ec. B1/Ec. 7 y LWSM 0704.1845 Ec. 54). No cambia el ancho, pero cambia σ(pp→ẽẽ) en un factor ~0.5–0.6. La fase 2 decidirá cuál reproduce σ = 5.97 fb.
- Internos: `gZeLLW = (g/c_W)(−1/2+s_W²)`, `gZeRLW = (g/c_W)s_W²`, `gZltRLW = gZeRLW + lwRep (gZeLLW − gZeRLW)`,
  `gMixLW = (gZeLLW − gZeRLW) MeLW/MLW = −(g/c_W)(1/2)(m_e/M)`.

## Convenciones y elecciones de signo

1. **Signo global del Z.** SM.fr usa D_μ = ∂_μ − i g T·W − i g′ Y B, que da
   L ⊃ +Z_μ [g_Z^{eL} ē_L γ^μ e_L + g_Z^{eR} ē_R γ^μ e_R] (vértice FR: +i g_Z γ^μ P),
   es decir, el signo global **opuesto** al de la Ec. (1). La Ec. (1) se traslada a la convención de SM.fr con Z → −Z
   (se invierten todos los acoplamientos al Z a la vez; los signos relativos se conservan). Es una convención y no cambia ningún observable.
2. **Signo LW (`etaLW`).** Los acoplamientos ẽẽγ y ẽẽZ llevan el factor `etaLW = −1` relativo al electrón
   (vértices FR: ẽẽγ = −i e·etaLW γ^μ, ẽẽZ = i·etaLW(g_L γ^μP_L + g_{ẽR} γ^μP_R)). En la producción por pares hay un solo vértice ẽẽV,
   así que el signo es una fase global de la amplitud y |M|² no cambia. Advertencia: el UFO es de norma positiva (propagador estándar).
   En la teoría LW real el signo del acoplamiento y el del propagador de norma negativa se combinan. Por eso, para procesos con dos o más
   vértices sobre la misma línea ẽ (p. ej. un fotón emitido desde ẽ), `etaLW = +1` es la elección consistente con la invariancia gauge.
   Para el LO de la señal da igual.
3. **Hermiticidad del término de mezcla.** Con coeficiente real, la Ec. (1) literal, X − X† con X = ē_R γ^μ ẽ_R, es **anti-hermítica**
   en una QFT de norma positiva. `CheckHermiticity[LMixLiteral]` lo confirma: devuelve los vértices ±2i·gMixLW γ^μP_R.
   La forma correcta, que sale de diagonalizar la Ec. A2 de Alvarez et al., es la hermítica **X + X†**, y es la que se implementa.
   `CheckHermiticity[LLW]` y `CheckHermiticity[LSM+LLW]` devuelven `{}`. El ancho no cambia porque |A|² es el mismo.
4. Solo se incluye el término de mezcla NC de la Ec. (1), así que **BR(ẽ → Z e) = 1**, como supone el artículo.

## Cómo volver a correrlo

```bash
cd /Users/danielamerizalde/Downloads/lee-wick/lw-cms-opendata/model
WS=/Applications/Wolfram.app/Contents/MacOS/wolframscript
$WS -file sanity_sm.wls > logs/sanity_sm.log      # ~1 min, debe imprimir "SANITY: PASS"
$WS -file run_fr.wls    > logs/run_fr.log         # ~3 min, reescribe LWElectron_UFO/
mv -f LWElectron_UFO.log logs/; rm -f py.py       # FR deja estos archivos en model/
python3 mg5_widths.py                             # ~1 min, MG5 compute_widths
```
Hay que usar **solo** FeynRules parcheado (`../../feynrules-patched`); el 2.3.49 original falla en silencio con MMA 15.
Los scripts fijan `FR$Parallelize = False`.
En MG5: `import model /Users/danielamerizalde/Downloads/lee-wick/lw-cms-opendata/model/LWElectron_UFO` (ruta absoluta).

## Resultados

Esquema EW por defecto de SM.fr: entradas `aEWM1 = 127.9`, `Gf = 1.16637e-5`, `MZ = 91.1876`.
Derivados: M_W = 79.824 GeV, s_W² = 0.23370, g/c_W = e/(s_W c_W) = 0.74070. ħc = 1.97327e-13 GeV·mm.

| m_e (GeV) | M (GeV) | Γ_FR (GeV) | Γ_MG5 (GeV) | cτ₀ (mm) | λ artículo (mm) | cτ₀/λ |
|---|---|---|---|---|---|---|
| 5.0e-4 | 200 | 7.28775e-12 | 7.2877e-12 | 2.70765e-2 | 2.70765e-2 | 1.000001 |
| 5.0e-4 | 300 | 1.20102e-11 | 1.2010e-11 | 1.64300e-2 | 1.64300e-2 | 1.000000 |
| 5.0e-4 | 400 | 1.62795e-11 | 1.6280e-11 | 1.21212e-2 | 1.21212e-2 | 0.999999 |
| 5.0e-4 | 500 | 2.04432e-11 | 2.0443e-11 | 9.65243e-3 | 9.65243e-3 | 1.000000 |
| 5.11e-4 | 200 | 7.61194e-12 | 7.6119e-12 | 2.59234e-2 | 2.70765e-2 | 0.957412 |
| 5.11e-4 | 300 | 1.25444e-11 | 1.2544e-11 | 1.57303e-2 | 1.64300e-2 | 0.957411 |
| 5.11e-4 | 400 | 1.70037e-11 | 1.7004e-11 | 1.16050e-2 | 1.21212e-2 | 0.957410 |
| 5.11e-4 | 500 | 2.13526e-11 | 2.1353e-11 | 9.24134e-3 | 9.65243e-3 | 0.957411 |

- Γ_FR sale de `ComputeWidths`/`TotWidth` de FeynRules, que coincide exactamente con la fórmula analítica
  Γ = c² M³/(32π m_Z²)(1−x)²(1+2x) con x = m_Z²/M² y c = (g/c_W)(1/2)(m_e/M), para Me del SM → 0. `run_fr.wls` lo verifica simbólicamente (diferencia = 0).
- MG5 coincide con FR dentro de su precisión impresa de 5 cifras (|Γ_MG5/Γ_FR − 1| < 4e-5). BR(ẽ→e Z) = 1 en ambos.
- **Interpretación de la razón 0.957.** La razón es constante e igual a (0.5/0.511)² = 0.95741. El artículo usó m_e = 0.5 MeV en el acoplamiento
  de mezcla, junto con el esquema EW por defecto de SM.fr (aEWM1, Gf, MZ). Con `MeLW = 5.0e-4`, λ se reproduce a 1e-6.

## Advertencias

- En el LWSM completo, ẽ también decae a W ν y a h e (Γ(h e) ≈ Γ(Z e) a M grande; BR(Z e) ≈ 0.71–0.53 para M = 200–500 GeV).
  Aquí se omiten a propósito, siguiendo al artículo, y por eso BR(Z e) = 1.
- No se incluyen el compañero LW del neutrino, los de los quarks ni el doblete LW completo: es un modelo mínimo para esta señal.
- `lwRep` cambia la sección eficaz de producción, no el ancho. El valor por defecto (0) es la Ec. (1) literal y no está validado contra σ = 5.97 fb.
- El UFO es de norma positiva. El carácter acausal/LW no está en el propagador, solo en el signo `etaLW`. Ver el punto 2 de las convenciones.
- El SM está en gauge de Feynman (opción por defecto de SM.fr) y con el electrón masivo (Me = 5.11e-4 GeV, sin `Massless.rst`).
- La validación cubre solo el ancho y los vértices. No se han generado eventos ni calculado σ (eso es la fase 2).
