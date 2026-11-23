#!/usr/bin/env python3
"""Shape comparison (area = 1): paper Fig. 2 signal (digitized), our Lee-Wick signal (v2, causal with
kappa -> -kappa) and our QCD from data (SS x R). Reads the two JSONs already produced:
mejoras/plots_final/signal_kappa_v2_causal_all.json and qcd/plots/qcd_numeros.json.
Usage (from phase3/analysis):  .venv/bin/python qcd/plot_senal_paper_qcd.py
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, '..', 'mejoras', 'plots_final', 'signal_kappa_v2_causal_all.json')))
P = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_signal_digitized.json')))
Q = json.load(open(os.path.join(HERE, 'plots', 'qcd_numeros.json')))
B = np.array(P['bins'], float)
assert np.allclose(B, S['bins']) and np.allclose(B, Q['hist']['bins'])
pn = np.array(P['paper_signal_x1000'], float); pn /= pn.sum()
hs = np.array(S['counts'], float); es = np.sqrt(hs) / hs.sum(); hs /= hs.sum()
R = Q['R_usado']['R']
nq = np.array(Q['hist']['QCD'], float) / R          # raw SS vertex counts
eq = np.sqrt(nq) / nq.sum(); hq = nq / nq.sum()
c = 0.5 * (B[1:] + B[:-1]); st = lambda h: np.append(h, h[-1])

fig, ax = plt.subplots(figsize=(10, 6.2))
ax.bar(c, hq, width=B[1] - B[0], color='#bbbbbb', label='QCD desde datos (SS): %d vértices, %.2f fb⁻¹' % (round(nq.sum()), Q['L_pb'] / 1000))
ax.errorbar(c[nq > 0], hq[nq > 0], yerr=eq[nq > 0], fmt='none', ecolor='#777', lw=1, capsize=2)
ax.step(B, st(pn), where='post', color='#D9653B', lw=2.6, ls='--', label='Señal, paper Fig. 2 (leído de la figura)')
ax.step(B, st(hs), where='post', color='#534AB7', lw=2, label='Señal, nuestra (causal, κ → −κ): %d vértices' % S['vertices'])
ax.errorbar(c[hs > 0], hs[hs > 0], yerr=es[hs > 0], fmt='none', ecolor='#534AB7', lw=1, capsize=2)
ax.set_yscale('log'); ax.set_ylim(3e-4, 1.5); ax.set_xlim(B[0], B[-1]); ax.axvline(0, color='#888', lw=0.8)
ax.set_xlabel('κ∥ = L_T · P_T (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('Formas de κ∥: señal Lee–Wick (paper y nuestra) y QCD desde datos', fontsize=13)
ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout(); out = os.path.join(HERE, 'plots', 'senal_paper_vs_nuestra_con_qcd.png'); fig.savefig(out, dpi=140, facecolor='white')
print('saved', out, '| QCD vertices', nq.sum(), 'f(k<0)', hq[:15].sum())
