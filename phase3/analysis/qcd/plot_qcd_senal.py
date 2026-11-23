#!/usr/bin/env python3
"""Overlays the Lee-Wick signal kappa_par (v2 thesis method: causal sample, kappa -> -kappa for SVs of a
truth-matched signal electron, isOS, every SV with L_T > 0.02 mm) on the QCD-from-data plot
(qcd/plots/qcd_numeros.json, written by qcd_desde_datos.py). The signal has no absolute normalization, so
it is drawn as a SHAPE scaled to the number of data-OS vertices.
Usage (from phase3/analysis):  .venv/bin/python qcd/plot_qcd_senal.py
"""
import glob, os, json, re
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'plots', 'qcd_numeros.json')))
B = np.array(J['hist']['bins']); h_os = np.array(J['hist']['datos_OS']); h_qcd = np.array(J['hist']['QCD'])
R = J['R_usado']['R']; L = J['L_pb']

files = sorted(glob.glob(os.path.join(HERE, '..', 'out', 'sig_causal', 'lw_zonly_M200_causal_b[0-9][0-9][0-9]_AODSIM.root')))
k = []
for f in files:
    for e in ak.to_list(uproot.open(f)['wdv/events'].arrays(filter_name=['isOS', 'e_sig', 'sv_k', 'sv_LT', 'sv_ele'])):
        if e['isOS'] != 1: continue
        for v in range(len(e['sv_k'])):
            if e['sv_LT'][v] <= 0.02: continue
            k.append((-1. if e['e_sig'][e['sv_ele'][v]] else 1.) * e['sv_k'][v])
k = np.array(k)
h_sig = np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)
scale = h_os.sum() / h_sig.sum()
c = 0.5 * (B[1:] + B[:-1])

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(c, h_qcd, width=B[1] - B[0], color='#bbbbbb', label='QCD desde datos: SS × R (R = %.2f)' % R)
ax.step(B, np.append(h_sig * scale, h_sig[-1] * scale), where='post', color='#534AB7', lw=2,
        label='Señal Lee–Wick (causal, κ → −κ), %d vértices, forma escalada a datos OS' % len(k))
ax.errorbar(c, h_os, yerr=np.sqrt(h_os), fmt='ko', ms=4, label='Datos OS (%d vértices)' % h_os.sum())
ax.set_yscale('symlog', linthresh=1); ax.set_xlim(B[0], B[-1])
ax.set_xlabel('κ∥ = L_T · P_T (mm·GeV)'); ax.set_ylabel('vértices / %g mm·GeV' % (B[1] - B[0]))
ax.set_title('Vértices con L_T > 0.02 mm, %.0f pb⁻¹' % L); ax.axvline(0, color='#888', lw=0.8)
ax.legend(frameon=False, fontsize=9, loc='upper left'); ax.grid(alpha=0.2)
fig.tight_layout(); out = os.path.join(HERE, 'plots', 'kappa_qcd_senal.png'); fig.savefig(out, dpi=140, facecolor='white')
print('saved', out)
print('señal: %d vértices, f(k<0)=%.3f, |k|<10: %.3f ; escala=%.4f' % (len(k), (k < 0).mean(), (np.abs(k) < 10).mean(), scale))
print('datos OS |k|<10: %.3f ; QCD |k|<10: %.3f' % (h_os[14:16].sum() / h_os.sum(), h_qcd[14:16].sum() / h_qcd.sum()))
