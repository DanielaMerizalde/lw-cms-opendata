# Guion para la reunión — avances Lee–Wick / CMS Open Data

Presentación: «Avances Lee–Wick CMS» (cada diapositiva tiene notas del orador con el texto completo).

## Los 4 mensajes clave (si sólo puedes decir cuatro cosas)

1. **Reprodujimos desde cero la teoría y la simulación del artículo, y coincide.**
   La longitud de vuelo λ del electrón de Lee–Wick coincide con la Tabla 1 en las 6 cifras que publica el artículo (toda su precisión),
   y la sección eficaz al ~1 %.

2. **La IA descubrió, sólo con los números del artículo, cosas que el artículo no dice:**
   - el autor usó mₑ = 0.5 MeV (redondeada);
   - calculó la señal **sin el fotón** (un electrón con carga debe acoplarse al fotón → la señal real es ~7 veces mayor);
   - la ecuación 1 tiene erratas.
   La tesis de 2022 lo confirmó todo en su código (Anexo A).

3. **La cadena completa de CMS 2012 funciona en mi computadora** (Docker + CMSSW_5_3_32):
   la señal atraviesa Geant4, el trigger con pile-up y la reconstrucción, y el vértice desplazado
   se conserva. Ya están los 40 bloques de señal; el análisis de datos reales está en curso.

4. **Evaluación de la IA:** hizo prácticamente todo el código y el cómputo; acertó en las deducciones
   importantes; también se equivocó (κ∥ en 3D en vez de transversal, tiempos de cómputo) y necesitó
   mis decisiones (escenario físico, estadística, alcance, aportar la tesis).

## Preguntas probables y cómo responder

- **¿Por qué no incluiste el fotón si es lo correcto?**
  Para reproducir primero exactamente lo que hizo el artículo. El escenario con fotón ya está calculado
  (fase 2) y es el siguiente paso con la simulación del detector.

- **¿Qué es κ∥?** El producto escalar, en el plano transversal, entre el desplazamiento del vértice
  (punto de colisión → vértice secundario) y el momento total de sus partículas.
  Positivo = desintegración normal; negativo = vértice «al revés» (acausal).

- **¿Cuánta señal hay?** Con la normalización del artículo, ~68 eventos producidos en 2012
  (la tesis no multiplicó por BR(Z→hadrones)² ≈ 0.49; con él serían ~33). Tras todos los cortes
  la tesis queda con 0.024 eventos: es una prueba de método, no una búsqueda.

- **¿Por qué sólo 1 % de los datos?** Se leen por internet desde el CERN y la Mac emula el software
  de 2012. Además, los fondos simulados sólo tienen un archivo en línea; el resto está en cinta.
  Para más estadística: pedir al portal de CERN Open Data que active esos archivos, o usar un clúster x86.

- **¿Cómo sabes que la IA no inventó resultados?** Cada número clave se obtuvo por al menos dos vías
  independientes (analítica, FeynRules, MadGraph) y la tesis confirmó las deducciones. Todo el código,
  los registros y tres informes en PDF están en la carpeta del proyecto.

- **¿Qué tan rápido fue?** Unos 3 días de calendario para las fases 1–2 y la cadena de la fase 3.

## Las 3 decisiones que pedir al director

1. ¿Solicitamos a CERN Open Data los archivos de fondos que están en cinta?
2. ¿Hay acceso a un clúster x86 (3–5 veces más rápido, sin emulación)?
3. ¿Extendemos a la física correcta (γ + Z, canal ℓ̃ → h e) como resultado propio?

## Resultados preliminares de la fase 3 (diapositivas 21 a 24)

Procesado: ~1 % de los datos de 2012 (43 archivos, ≈ 113 pb⁻¹), un archivo por fondo, 500 + 500 eventos de señal.

- **La mayoría de los cortes coinciden con la tesis** (trigger, trazas, carga opuesta).
- **Dos cortes no se reproducen:** DRC (tesis 0.99, nosotros 0.24) e IPP (tesis 0.003, nosotros 0.4–0.6).
  Con lo que está escrito en la tesis no se puede llegar a sus números → probablemente usó condiciones
  no descritas. **Buena pregunta para el director:** ¿se sabe qué más se aplicó?
- **κ∥ en datos:** simétrico (53 % negativos), como se espera del fondo.
- **El mensaje más interesante:** si se toma el vértice que cae sobre la desintegración real,
  el 86 % de los acausales tiene κ∥ < 0 frente al 24 % de los causales → **la variable funciona**.
  Pero sólo ~15 % de los vértices reconstruidos son correctos; el resto son combinaciones electrón + jets
  equivocadas que borran la asimetría. Siguiente paso: identificar bien los jets del Z.
- **El atajo del artículo** (invertir el signo de κ∥) no equivale a simular de verdad el vértice reflejado.

Si preguntan por la comparación datos/fondos: el fondo simulado tiene poquísima estadística (un archivo
por muestra; cada evento de DY pesa ~34), por eso la figura tiene picos; hace falta pedir el resto a CERN.
