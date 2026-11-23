#!/usr/bin/env python3
"""kappa_par of our simulated LW signal (v3 final selection, L_T > 0.02 mm) against the signal curve of
the paper's Fig. 2, digitized from the figure (docs/figuras_p1/paper_signal_digitized.json).
Both are normalised to unit area, with the paper's binning (-150..150 mm GeV, 10 per bin).
Paper bins at the bottom edge of its plot (~0.41) are drawn as upper limits.
Usage: ../.venv/bin/python plot_signal_vs_paper.py
"""
import glob, os, json, importlib.util, io, contextlib
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('cr', os.path.join(HERE, 'control_regions.py'))
cr = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(cr)

def kappas(sample):
    k = []
    for f in sorted(glob.glob(os.path.join(HERE, 'out_data', sample, '*.root'))):
        for e in ak.to_list(uproot.open(f)['wdv3/events'].arrays(filter_name=['isOS', 'genW', 'pvx', 'pvy', 'e_*', 'c_*', 'f_*'])):
            if e['isOS'] != 1: continue
            k += [x['k'] for x in cr.svs(e) if x['chi2'] < cr.CHI2MAX and x['LT'] > 0.02]
    return np.array(k)

pap = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_signal_digitized.json')))
B = np.array(pap['bins'], float); c = 0.5 * (B[1:] + B[:-1])
pv = np.array(pap['paper_signal_x1000'], float); floor = pv <= 0.41
kc = -kappas('sig_causal')     # paper convention: causal signal with kappa -> -kappa
ka = kappas('sig_acausal')     # ours: vertex reflected before the detector
H = lambda k: np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)
hc, ha = H(kc), H(ka)

fig, ax = plt.subplots(figsize=(10, 6.2))
pn = pv / pv.sum()
ax.step(B, np.append(pn, pn[-1]), where='post', color='#D9653B', lw=2.4, ls='--', label='Paper, Fig. 2 (leído de la figura)')
ax.scatter(c[floor], pn[floor], marker='v', color='#D9653B', s=40, zorder=3, label='Paper: en el borde inferior de su gráfica (≤)')
hs = hc + ha
ax.step(B, np.append(hc / hc.sum(), (hc / hc.sum())[-1]), where='post', color='#185FA5', lw=2, label='Nuestra señal causal con κ → −κ (N=%d)' % len(kc))
ax.step(B, np.append(ha / ha.sum(), (ha / ha.sum())[-1]), where='post', color='#1D9E75', lw=2, ls=':', label='Nuestra señal acausal reflejada (N=%d)' % len(ka))
ax.set_yscale('log'); ax.set_ylim(3e-4, 1.5); ax.set_xlim(-150, 150)
ax.set_xlabel('κ∥ (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('Señal Lee–Wick (M = 200 GeV): nuestro κ∥ frente al del paper', fontsize=13)
ax.axvline(0, color='#888', lw=0.8); ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout()
out = os.path.join(HERE, 'plots_final', 'signal_kappa_vs_paper.png'); fig.savefig(out, dpi=140, facecolor='white')
f = lambda k: (k < 0).mean()
print('saved', out)
print('paper: frac kappa<0 = %.3f, central two bins = %.3f' % (pv[:15].sum() / pv.sum(), pn[14] + pn[15]))
print('ours causal(-k): N=%d frac<0=%.3f central=%.3f median|k|=%.2f' % (len(kc), f(kc), (hc[14] + hc[15]) / hc.sum(), np.median(abs(kc))))
ks=np.concatenate([kc,ka]); print('ours combined: N=%d frac<0=%.3f central=%.3f' % (len(ks), f(ks), (hs[14]+hs[15])/hs.sum()))
print('ours acausal:    N=%d frac<0=%.3f central=%.3f median|k|=%.2f' % (len(ka), f(ka), (ha[14] + ha[15]) / ha.sum(), np.median(abs(ka))))
