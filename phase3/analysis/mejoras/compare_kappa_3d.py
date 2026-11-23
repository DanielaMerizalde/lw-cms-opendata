#!/usr/bin/env python3
"""Signal kappa_par (thesis method v2, causal sample with kappa -> -kappa) computed in the transverse plane
(sv_k, as the thesis text says) and in 3D (sv_k3trk = 10*(L.P) with z included), against the paper's signal
curve digitized from Fig. 2. Unit area, paper binning.   Usage: ../.venv/bin/python compare_kappa_3d.py
"""
import glob, os, json
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

def kap(sample, br, flip):
    k = []
    for f in sorted(glob.glob(os.path.join(HERE, '..', 'out', sample, '*.root'))):
        for e in ak.to_list(uproot.open(f)['wdv/events'].arrays(filter_name=['isOS', 'e_sig', 'sv_LT', 'sv_ele', br])):
            if e['isOS'] != 1: continue
            for v in range(len(e[br])):
                if e['sv_LT'][v] <= 0.02: continue
                s = -1. if (flip and e['e_sig'][e['sv_ele'][v]]) else 1.
                k.append(s * e[br][v])
    return np.array(k)

pap = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_signal_digitized.json')))
B = np.array(pap['bins'], float); c = 0.5 * (B[1:] + B[:-1])
pv = np.array(pap['paper_signal_x1000'], float); pn = pv / pv.sum()
H = lambda k: np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)

kT, k3 = kap('sig_causal', 'sv_k', True), kap('sig_causal', 'sv_k3trk', True)
hT, h3 = H(kT) / len(kT), H(k3) / len(k3)
st = lambda h: np.append(h, h[-1])
fig, ax = plt.subplots(figsize=(10, 6.2))
ax.step(B, st(pn), where='post', color='#D9653B', lw=2.6, ls='--', label='Paper, Fig. 2 (leído de la figura)')
ax.step(B, st(hT), where='post', color='#888780', lw=2, ls=':', label='Nuestra señal, κ∥ transversal (x, y)  N=%d' % len(kT))
ax.step(B, st(h3), where='post', color='#534AB7', lw=2.2, label='Nuestra señal, κ en 3D (x, y, z)  N=%d' % len(k3))
ax.set_yscale('log'); ax.set_ylim(3e-4, 1.5); ax.set_xlim(-150, 150)
ax.set_xlabel('κ (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('Señal Lee–Wick (método de la tesis, causal con κ → −κ): ¿κ transversal o en 3D?', fontsize=12.5)
ax.axvline(0, color='#888', lw=0.8); ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout()
out = os.path.join(HERE, 'plots_final', 'signal_kappa_2d_vs_3d.png'); fig.savefig(out, dpi=140, facecolor='white')
print('saved', out)
tail = lambda h, lo: h[np.abs(c) > lo].sum()
print('                 central(|k|<10)  |k|>50   |k|>100  frac<0   nonzero bins')
print('paper            %.3f            %.4f   %.4f   %.3f    %d/30' % (pn[np.abs(c) < 10].sum(), tail(pn, 50), tail(pn, 100), pn[c < 0].sum(), (pn > 0).sum()))
for n, k, h in [('transversal', kT, hT), ('3D', k3, h3)]:
    print('%-16s %.3f            %.4f   %.4f   %.3f    %d/30' % (n, h[np.abs(c) < 10].sum(), tail(h, 50), tail(h, 100), (k < 0).mean(), (h > 0).sum()))
