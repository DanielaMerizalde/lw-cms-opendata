#!/usr/bin/env python3
"""Signal kappa_par (transverse, L_T * P_T) with the thesis-style selection (v2) on ALL causal blocks
(b000-b019, 25 ev each, plus the 2026-11-08 extension b020-b059, 50 ev each), with the thesis flip
(kappa -> -kappa for SVs of a truth-matched signal electron), against the paper's Fig. 2 signal curve.
Same selection as compare_signal_methods.py (isOS, every SV with L_T > 0.02 mm); causal sample only.
Usage: ../.venv/bin/python compare_signal_causal_all.py
"""
import glob, os, json, re
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(HERE, '..', 'out', 'sig_causal', 'lw_zonly_M200_causal_b[0-9][0-9][0-9]_AODSIM.root')))
NPER = lambda f: 25 if int(re.search(r'_b(\d{3})_', f).group(1)) < 20 else 50
ncoll = sum(NPER(f) for f in files)

k = []; nos = 0
for f in files:
    for e in ak.to_list(uproot.open(f)['wdv/events'].arrays(filter_name=['isOS', 'e_sig', 'sv_k', 'sv_LT', 'sv_ele'])):
        if e['isOS'] != 1: continue
        nos += 1
        for v in range(len(e['sv_k'])):
            if e['sv_LT'][v] <= 0.02: continue
            k.append((-1. if e['e_sig'][e['sv_ele'][v]] else 1.) * e['sv_k'][v])
k = np.array(k)

pap = json.load(open(os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_p1', 'paper_signal_digitized.json')))
B = np.array(pap['bins'], float)
pv = np.array(pap['paper_signal_x1000'], float); pn = pv / pv.sum()
h = np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)
hn = h / h.sum(); err = np.sqrt(h) / h.sum()
c = 0.5 * (B[1:] + B[:-1])
nz = int((h > 0).sum())

fig, ax = plt.subplots(figsize=(10, 6.2))
ax.step(B, np.append(pn, pn[-1]), where='post', color='#D9653B', lw=2.6, ls='--', label='Paper, Fig. 2 (leído de la figura)')
ax.step(B, np.append(hn, hn[-1]), where='post', color='#534AB7', lw=2,
        label='Tesis (v2), causal con κ → −κ: %d vértices, %d colisiones' % (len(k), ncoll))
ax.errorbar(c[h > 0], hn[h > 0], yerr=err[h > 0], fmt='none', ecolor='#534AB7', lw=1, capsize=2)
ax.set_yscale('log'); ax.set_ylim(3e-4, 1.5); ax.set_xlim(B[0], B[-1])
ax.set_xlabel('κ∥ = L_T · P_T (mm·GeV)', fontsize=13); ax.set_ylabel('fracción de vértices por intervalo (área = 1)', fontsize=12)
ax.set_title('Señal Lee–Wick (método de la tesis): %d de %d intervalos con entradas' % (nz, len(h)), fontsize=13)
ax.axvline(0, color='#888', lw=0.8); ax.legend(fontsize=10, frameon=False, loc='upper right'); ax.grid(alpha=0.2)
fig.tight_layout()
out = os.path.join(HERE, 'plots_final', 'signal_kappa_v2_causal_all_vs_paper.png'); fig.savefig(out, dpi=140, facecolor='white')

cen = lambda x: (x[14] + x[15]) / x.sum()
res = dict(blocks=len(files), collisions=ncoll, os_events=nos, vertices=int(len(k)), nonzero_bins=nz, nbins=len(h),
           frac_neg=float((k < 0).mean()), central=float(cen(h)), frac_abs_gt50=float((abs(k) > 50).mean()),
           paper=dict(frac_neg=float(pv[:15].sum() / pv.sum()), central=float(cen(pv)),
                      frac_abs_gt50=float((pv[:10].sum() + pv[20:].sum()) / pv.sum())),
           counts=h.astype(int).tolist(), bins=B.tolist())
json.dump(res, open(os.path.join(HERE, 'plots_final', 'signal_kappa_v2_causal_all.json'), 'w'), indent=1)
print('saved', out)
print('bloques=%d colisiones=%d eventos_OS=%d vertices=%d intervalos_no_vacios=%d/%d' % (len(files), ncoll, nos, len(k), nz, len(h)))
print('v2 causal flip: frac<0=%.3f central=%.3f frac|k|>50=%.3f' % (res['frac_neg'], res['central'], res['frac_abs_gt50']))
print('paper:          frac<0=%.3f central=%.3f frac|k|>50=%.3f' % (res['paper']['frac_neg'], res['paper']['central'], res['paper']['frac_abs_gt50']))
print('counts', res['counts'])
