#!/usr/bin/env python3
"""Shape comparison (area = 1) of kappa_par: our data OS and our QCD from data (SS x R, qcd/plots/qcd_numeros.json)
vs the paper's Fig. 2 data points and QCD-multijet fill, digitized by docs/figuras_p1/digitalizar_fig2.py
(docs/figuras_p1/paper_fig2_datos_qcd.json).
Note: our first/last bins include the overflow (np.clip); the paper's are read as drawn.
Usage (from phase3/analysis):  .venv/bin/python qcd/plot_paper_datos_qcd.py
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
Q = json.load(open(os.path.join(HERE, 'plots', 'qcd_numeros.json')))
P = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_fig2_datos_qcd.json')))
B = np.array(P['bins'], float); assert np.allclose(B, Q['hist']['bins'])
c = 0.5 * (B[1:] + B[:-1]); st = lambda h: np.append(h, h[-1])
L = Q['L_pb']

nd = np.array(Q['hist']['datos_OS'], float)
R = Q['R_usado']['R']; nq_raw = np.array(Q['hist']['QCD'], float) / R    # raw SS vertex counts (for errors)
pd = np.array(P['paper_data'], float); pq = np.array(P['paper_qcd'], float)

def frac(h): return h / h.sum()
hd, hq, hpd, hpq = frac(nd), frac(nq_raw), frac(pd), frac(pq)
ed = np.sqrt(nd) / nd.sum(); eq = np.sqrt(nq_raw) / nq_raw.sum(); epd = np.sqrt(pd) / pd.sum()

def summ(h):
    return h[:15].sum(), h[14:16].sum()      # f(k<0), f(|k|<10)
rows = [('Datos, nuestros', nd), ('Datos, paper', pd), ('QCD, nuestro', nq_raw), ('QCD, paper', pq)]
for name, h in rows:
    fn, fc = summ(frac(h)); print(f'{name:16s} N={h.sum():8.1f}  f(k<0)={fn:.3f}  f(|k|<10)={fc:.3f}')
print(f'QCD/datos: nuestro {np.sum(Q["hist"]["QCD"]) / nd.sum():.3f}  paper {pq.sum() / pd.sum():.3f}')
print(f'vértices por pb^-1: nuestros {nd.sum() / L:.3f}  paper {pd.sum() / 11500:.3f}')

fig, ax = plt.subplots(figsize=(11, 6.6))
ax.bar(c, hq, width=10, color='#c8c8c8', label='QCD, nuestro (SS, %d vértices, %.2f fb⁻¹)' % (round(nq_raw.sum()), L / 1000))
ax.step(B, st(hpq), where='post', color='#D9653B', lw=2.4, ls='--', label='QCD, paper (Fig. 2)')
m = nd > 0
ax.errorbar(c[m], hd[m], yerr=ed[m], fmt='o', color='black', ms=6, capsize=2, label='Datos OS, nuestros (%d vértices)' % nd.sum())
m = pd > 0
ax.errorbar(c[m] + 1.5, hpd[m], yerr=epd[m], fmt='o', mfc='white', mec='#C4252E', ecolor='#C4252E', mew=1.8, ms=7,
            capsize=2, label='Datos, paper (Fig. 2, %d vértices, 11.5 fb⁻¹)' % round(pd.sum()))
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.2); ax.set_xlim(B[0], B[-1]); ax.axvline(0, color='#888', lw=0.8)
ax.set_xlabel('κ∥ = L_T · P_T (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('κ∥: nuestros datos y QCD vs los del paper (formas)', fontsize=13)
ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout(); out = os.path.join(HERE, 'plots', 'paper_vs_nuestro_datos_qcd.png'); fig.savefig(out, dpi=140, facecolor='white')
print('saved', out)
