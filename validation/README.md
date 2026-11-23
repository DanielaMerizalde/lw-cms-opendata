# Validación teórica (fase 1): anchura y longitud de decaimiento del electrón LW

Reproducción independiente de la Tabla 1 de J. Sánchez, ACI 15(1) 2780 (2023), y contraste
con Álvarez, Da Rold, Schat, Szynkman, JHEP 10 (2009) 023 [arXiv:0908.2446] y
Grinstein, O'Connell, Wise, PRD 77 (2008) 025012 [arXiv:0704.1845].

Archivos:
- `width_analytic.py`: derivación (en el docstring) y todos los cálculos. Se ejecuta con `python3 -I validation/width_analytic.py`.
- `widths_schemes.csv`: Γ, cτ₀ y el cociente con el paper para cada esquema EW y cada valor de m_e.
- `ctau_vs_M.png`: puntos del paper frente a las curvas.

## 1. Fórmula

Para F(M) → f Z con acoplamiento quiral puro `-c Z_μ f̄ γ^μ P_R F + h.c.`, el resultado con masas completas es
Σ|A|² = c²[2p·P + 4(k·p)(k·P)/m_Z²]. Con m_f → 0 y x = m_Z²/M²:

    Γ = c² M³ /(32π m_Z²) (1-x)² (1+2x)

Aquí c = (g_Z^{eL} - g_Z^{eR}) m_e/M = -(g/c_W)(1/2)(m_e/M). El factor M³/m_Z² viene de la polarización longitudinal.
Si se toma (g/c_W)² = 4√2 G_F m_Z²:

    Γ(ℓ̃→Ze) = G_F m_e² M /(16√2 π) (1-x)²(1+2x)  →  y_e² M/(64π)   (M ≫ m_Z)

Esto coincide con Γ(ℓ̃→he) = y_e² M/(64π)(1-m_h²/M²)². Es la equivalencia de Goldstone, comprobada numéricamente
(cociente 1.00000 para M = 100 TeV). Con G_F como input, **Γ no depende ni de m_W ni de s_W**. El efecto de m_e en la
cinemática es de 2×10⁻¹¹ y se puede despreciar.

## 2. Esquemas EW: cociente R = (ħc/Γ_Z)/λ_paper

Los valores de R son los mismos en las cuatro masas (dispersión ≤ 2×10⁻⁶).

| Esquema | (g/c_W)² | R (m_e = 0.51099895 MeV) | R (m_e = 0.500 MeV) |
|---|---|---|---|
| (a) on-shell s_W² = 1 - m_W²/m_Z², con G_F | 0.54863 | 0.95741 | **1.00000** |
| (b) SM.fr de FeynRules/MG (aEWM1=127.9, Gf, MZ → MW=79.82, s_W²=0.2337) | 0.54863 | 0.95741 | **1.00000** |
| (c) MS-bar s_W²=0.2312, α(m_Z)=1/127.9 | 0.55276 | 0.95027 | 0.99253 |
| (d1) α(0)=1/137.036, s_W² on-shell (m_W=80.385) | 0.52941 | 0.99218 | 1.03631 |
| (d2) α(0), s_W²=0.2312 | 0.51591 | 1.01814 | 1.06343 |
| (e) g de G_F y m_W, c_W de MS-bar (inconsistente) | 0.55456 | 0.94719 | 0.98932 |

Ajuste libre Γ_paper = K·Γ_(a)(m_e^PDG; m_Z):
- K = 0.957414 y m_Z = 91.1873 GeV, con residuo máximo 4×10⁻⁷.
- √K · m_e^PDG = **0.50000 MeV**. Como comparación, (0.5/0.51099895)² = 0.957414.
- Mover m_Z a 91.19–91.2 GeV rompe la constancia en el sexto dígito. Los datos fijan m_Z = 91.1876.

**Conclusión:** el desfase del 4.3 % se explica exactamente si se usa **m_e = 0.5 MeV** con el esquema G_F estándar
(SM.fr: aEWM1=127.9, Gf=1.16637e-5, MZ=91.1876). λ es ħc/Γ(ℓ̃→Ze) en reposo, es decir cτ₀ propio, y cuenta **solo el canal Z**.
Ningún esquema EW razonable con m_e del PDG llega a R=1 y a la vez es constante. El caso d1 (R=0.992) es una coincidencia
y queda descartado por el ajuste.

### Recomendación para el agente del modelo
- Usar los parámetros EW de SM.fr (aEWM1=127.9, Gf=1.16637e-5, MZ=91.1876).
- Para reproducir la Tabla 1, **Me = 5.0e-4 GeV** en el acoplamiento de mezcla (m_e/M). Si el modelo usa Me=5.11e-4, cτ₀ sale un 4.3 % menor.
- Para reproducir λ, el ancho de ℓ̃ debe incluir solo ℓ̃→Ze. Las predicciones de referencia son cτ₀ = 27.0765, 16.4300, 12.1212 y 9.65243 μm.

## 3. Estimación del desplazamiento en el laboratorio (TOY, no es un cálculo con PDFs)

Hipótesis del toy: √ŝ muestreado con σ̂(ŝ)·ŝ^{-n}, n ∈ {3,4,5}, distribución angular 1+cos²θ, y βγ_T = p_T/M (invariante bajo boosts longitudinales).

| M (GeV) | cτ₀ (μm) | ⟨βγ_T⟩ | ⟨L_T⟩ (μm) | P(L_T > 20 μm) |
|---|---|---|---|---|
| 200 | 27.1 | 0.39–0.53 | 11–14 | 0.15–0.22 |
| 300 | 16.4 | 0.39–0.53 | 6–9 | 0.06–0.11 |
| 400 | 12.1 | 0.39–0.53 | 5–6 | 0.03–0.06 |
| 500 | 9.7 | 0.39–0.53 | 4–5 | 0.02–0.04 |

Con una banda conservadora βγ_T ∈ [0.3, 1.5], L_T ∈ [0.3, 1.5]·cτ₀. Incluso para M=200 GeV el desplazamiento medio
**está por debajo** de la resolución de ~20 μm, y solo la cola exponencial (~15–20 %) la supera. Álvarez et al. (Ec. 20)
expresan lo mismo como el corte p_T > M Δx Γ. Hay que confirmarlo con MadGraph: es un estimado.

## 4. Literatura

**(i) ¿La Ec. 1 coincide con Álvarez et al.?** Solo en parte.
- La Ec. 7 de Álvarez (base de sabor) tiene −(Z+Z̃)[g_L(ℓ̄_L γ ℓ_L − ℓ̃̄ γ ℓ̃) + g_R(ē_R γ e_R − ẽ̄ γ ẽ)]. Ahí ℓ̃ (el LW-doblete) es vectorial y se acopla con **g_L en ambas quiralidades**.
- La Ec. 1 de Sánchez sale de la Ec. B1 (base de masa), que tiene g_L Ē_L γ η E_L + g_R Ē_R γ η E_R + (g_L−g_R) Ē γ(S_L†S_L P_L − S_R†S_R P_R)E.
- Diagonalicé numéricamente la matriz simpléctica (A2) con η = diag(1,−1,−1) (`symplectic_check()`) y obtuve lo siguiente:
  - La mezcla ℓ̃–e es solo **R** a primer orden, con magnitud exactamente (g_L−g_R) m_e/M_ℓ. La componente L está suprimida (≲ ε²). El signo y la quiralidad de la mezcla coinciden, y el factor es m_e/M_ℓ (no depende de M_e).
  - En cambio, el término diagonal X_R[33] = 1 de la corrección cambia el acoplamiento de ℓ̃_R de −g_R a **−g_L**. La Ec. 1 omite esto y asigna −g_R a ℓ̃_R, lo que corresponde a la carga del singlete ẽ, no a la de ℓ̃.
  - Esto no afecta a Γ(ℓ̃→Ze), pero sí a la producción por Z. Una estimación partónica da σ(Ec. 1)/σ(doblete vectorial) ≈ 0.51–0.61. GOW, Ec. 54, confirma que Q̃_L y Q̃'_R se acoplan igual al campo gauge.
- El ℓ̃ de Sánchez es el de Álvarez: E³ ≃ ℓ̃_e, el compañero del doblete (Sec. V).

**(ii) Hermiticidad.** Tal como está escrita, ē_R γ ℓ̃_R − ℓ̃̄_R γ e_R con coeficiente real es **anti-hermítica**. En B1 la matriz X = S_R†·diag(0,0,1)·S_R es hermítica. Numéricamente X_R[1,3] = X_R[3,1], así que la forma correcta es (ē_R γ ℓ̃_R **+** ℓ̃̄_R γ e_R). El signo − no cambia |A|² en el decaimiento ni en la producción de pares, pero `CheckHermiticity` de FeynRules lo marcaría. Hay que usar "+ h.c." (los signos negativos de η solo aparecen en los términos diagonales LW).

**(iii) Otros canales.**
- Álvarez, Tabla II y Sec. IV.B: E³ → Ze y E³ → he están ambos controlados por y_e. E³ → Wν lleva una supresión extra m_e/M (amplitud ∝ m_e²/M²) y es despreciable. El patrón asintótico para el doblete es Z:h:W = 1:1:0.
- Con m_h = 125 GeV, BR(Ze) = 0.71, 0.59, 0.55 y 0.53 para M = 200–500 GeV. Por tanto τ_total < τ_Z por un factor 1.4–1.9.
- Para el singlete ẽ (E²) domina Wν (Sec. IV.A, Fig. 4a).
- Álvarez usan el **doblete** ℓ̃_e (Sec. V) y m_h = 200 GeV.
- La Tabla 1 de Sánchez equivale a BR(Ze)=1. Como ignora el canal h, λ está sobrestimado si m_h = 125.

**(iv) Números de Álvarez et al.**
- Γ ~ 10⁻¹¹ GeV para M ~ 300 GeV (Sec. II).
- τ(E³_e) = 4×10⁻¹⁴, 2×10⁻¹⁴ y 9×10⁻¹⁵ s para M = 300, 600 y 1000 GeV (m_h=200, Sec. IV.B).
  - Mi Z+h con m_e del PDG y m_h=200 da **3.99×10⁻¹⁴ s** a 300 GeV, lo que concuerda.
  - El paper de Sánchez da λ/c = 5.48×10⁻¹⁴ s (solo Z, m_e=0.5).
- σ_total (LHC **14 TeV**, con W̃,B̃ a 3 TeV) = 66.7, 27 y 15 fb para M = 300, 400 y 500 GeV (Tabla III).
- σ con corte (desplazamiento > 20 μm) = 11 y 3.5 fb (m_h=200).
- Concluyen que el canal es observable para M ≲ 450 GeV.
- No son directamente comparables con los 8 TeV de Sánchez (0.96 fb para M=300). El cociente ~70 parece grande incluso para 14 vs 8 TeV. Ver los temas abiertos.

**(v) Desplazamiento acausal.**
- Álvarez, Ec. 1 (= GOW arXiv:0805.2156, Ec. 46): ⟨ψ_out|ψ_in⟩ ∝ F̂(−Mω/√ω²) Ĝ(−Mω/√ω²) e^{iM√ω²} e^{−Γ√ω²/2}, con ω = z_D − z_P.
- El momento total de los productos satisface q ≈ −Mω/√ω², mientras que en el caso causal q ≈ +Mω/√ω².
- Es decir, el vértice secundario está desplazado **en sentido opuesto** al momento total visible. La magnitud se distribuye como exp(−Γ|ω|/2) en amplitud: la misma ley exponencial con longitud βγcτ₀ que en el caso causal, solo que invertida.
- GOW 0704.1845, Ec. 10: con la convención p²−M²+iMΓ, la anchura del campo LW es **negativa**, Γ_LW = −|Γ|. Por eso los polos están en la hoja física. El signo del propagador compensa el signo de Γ, y Im A > 0 (unitariedad).
- Implementación en MC: generar el decaimiento causal con |Γ| y reflejar el vector de desplazamiento, x_SV = x_PV − (p⃗/M) cτ₀ t con t ~ Exp(1). Equivale a invertir el signo de la paralelidad, que es lo que hizo Sánchez.

## 5. Temas abiertos
- Por qué se usó m_e = 0.5 MeV: probablemente un parámetro del modelo FeynRules de Sánchez (o un redondeo). La alternativa (otro factor ×0.957414) es muy improbable dado el acuerdo a 10⁻⁶, pero no puedo verificarlo sin su modelo.
- El acoplamiento Z de ℓ̃_R (g_R en la Ec. 1 frente a g_L en Álvarez/GOW) cambia σ en un factor ~0.5–0.6. Hay que comprobar con MG cuál reproduce σ(8 TeV) = 5.97 fb para M=200. Tampoco he verificado el signo relativo γ/Z de los acoplamientos LW (−eQ para ℓ̃): un signo inconsistente invertiría la interferencia.
- La estimación de βγ es un toy sin PDFs.
- El canal ℓ̃→he (no incluido en la Tabla 1) cambia la longitud de decaimiento total y el BR de la señal.
- Leí el texto de A7 con extracción PDF imperfecta. El signo de la mezcla y su hermiticidad los confirmé con la diagonalización numérica de (A2), no leyendo A7.
