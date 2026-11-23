#!/usr/bin/env python3
"""Signal kappa_par with the thesis-style selection (v2) and with ours (v3), against the paper's signal
curve digitized from Fig. 2. v2 follows the paper's definition of Fig. 2: SG stage (opposite-sign
electrons), every SV built from an electron + jet pair (SVRA + Table 2.1) with L_T > 0.02 mm, and the
thesis flip (kappa -> -kappa for SVs of a truth-matched signal electron). Unit area, paper binning.
Usage: ../.venv/bin/python compare_signal_methods.py
"""
import glob, os, json
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

def v2_kappas(sample, flip):
    k = []
    for f in sorted(glob.glob(os.path.join(HERE, '..', 'out', sample, '*.root'))):
        for e in ak.to_list(uproot.open(f)['wdv/events'].arrays(filter_name=['isOS', 'e_sig', 'sv_k', 'sv_LT', 'sv_ele'])):
            if e['isOS'] != 1: continue
            for v in range(len(e['sv_k'])):
                if e['sv_LT'][v] <= 0.02: continue
                sgn = -1. if (flip and e['e_sig'][e['sv_ele'][v]]) else 1.
                k.append(sgn * e['sv_k'][v])
    return np.array(k)

pap = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_signal_digitized.json')))
B = np.array(pap['bins'], float); c = 0.5 * (B[1:] + B[:-1])
pv = np.array(pap['paper_signal_x1000'], float); pn = pv / pv.sum()
H = lambda k: np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)

k2c = v2_kappas('sig_causal', flip=True)
k2a = v2_kappas('sig_acausal', flip=False)
h2c, h2a = H(k2c), H(k2a)

fig, ax = plt.subplots(figsize=(10, 6.2))
ax.step(B, np.append(pn, pn[-1]), where='post', color='#D9653B', lw=2.6, ls='--', label='Paper, Fig. 2 (leído de la figura)')
ax.step(B, np.append(h2c / h2c.sum(), (h2c / h2c.sum())[-1]), where='post', color='#534AB7', lw=2, label='Método de la tesis (v2): causal con κ → −κ (N=%d)' % len(k2c))
ax.step(B, np.append(h2a / h2a.sum(), (h2a / h2a.sum())[-1]), where='post', color='#888780', lw=2, ls=':', label='Método de la tesis (v2): acausal reflejada (N=%d)' % len(k2a))
ax.set_yscale('log'); ax.set_ylim(3e-4, 1.5); ax.set_xlim(-150, 150)
ax.set_xlabel('κ∥ (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('Señal Lee–Wick: el método de la tesis (v2) frente a la curva del paper', fontsize=13)
ax.axvline(0, color='#888', lw=0.8); ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout()
out = os.path.join(HERE, 'plots_final', 'signal_kappa_v2_vs_paper.png'); fig.savefig(out, dpi=140, facecolor='white')
f = lambda k: (k < 0).mean()
cen = lambda h: (h[14] + h[15]) / h.sum()
print('saved', out)
print('paper:           frac<0=%.3f central=%.3f  frac|k|>50=%.3f' % (pv[:15].sum() / pv.sum(), cen(pv), (pv[:10].sum() + pv[20:].sum()) / pv.sum()))
for name, k, h in [('v2 causal flip', k2c, h2c), ('v2 acausal', k2a, h2a)]:
    print('%-16s N=%d frac<0=%.3f central=%.3f frac|k|>50=%.3f' % (name, len(k), f(k), cen(h), (abs(k) > 50).mean()))
