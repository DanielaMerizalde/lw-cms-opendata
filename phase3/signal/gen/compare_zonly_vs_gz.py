#!/usr/bin/env python3
"""compare_zonly_vs_gz.py -- truth-level comparison of the Z-only signal (phase 3A, paper normalisation)
with the gamma+Z sample of phase 2B (generation/events/samples/M200), M = 200 GeV.

Variables: elw beta*gamma, beta*gamma_T, L, L_T (from SV-PV), final-electron pT, eta, truth-jet pT, eta
(anti-kT 0.5, pT>20, |eta|<4.7, built by the Pythia driver), number of truth jets, and the fraction
of elw with L_T > 20 um.  Two-sample Kolmogorov-Smirnov test (scipy.stats.ks_2samp).

Usage: python3 compare_zonly_vs_gz.py ZONLY_DIR GZ_DIR OUT_DIR
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import ks_2samp  # noqa: E402

zdir, gdir, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)


def load(d, M=200):
    e = np.genfromtxt(os.path.join(d, 'truth_M%d_elw.csv' % M), delimiter=',', names=True)
    j = np.genfromtxt(os.path.join(d, 'truth_M%d_jets.csv' % M), delimiter=',', names=True)
    return e, j


def eta(px, py, pz):
    p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
    return 0.5 * np.log((p + pz) / np.maximum(p - pz, 1e-12))


def variables(e, j):
    v = {}
    p = np.sqrt(e['px'] ** 2 + e['py'] ** 2 + e['pz'] ** 2)
    v['betagamma'] = p / e['m']
    v['betagamma_T'] = np.hypot(e['px'], e['py']) / e['m']
    dx, dy, dz = e['xd'] - e['xp'], e['yd'] - e['yp'], e['zd'] - e['zp']
    v['L_um'] = 1e3 * np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    v['LT_um'] = 1e3 * np.hypot(dx, dy)
    v['e_pT'] = np.hypot(e['ef_px'], e['ef_py'])
    v['e_eta'] = eta(e['ef_px'], e['ef_py'], e['ef_pz'])
    v['jet_pT'] = np.hypot(j['px'], j['py'])
    v['jet_eta'] = eta(j['px'], j['py'], j['pz'])
    ev = j['iev'].astype(int)
    nev = int(e['iev'].max()) + 1
    v['n_jets'] = np.bincount(ev, minlength=nev).astype(float)
    return v


vz = variables(*load(zdir))
vg = variables(*load(gdir))
spec = {'betagamma': (r'$\beta\gamma$ ($\tilde e$)', np.linspace(0, 8, 41)),
        'betagamma_T': (r'$\beta\gamma_T$ ($\tilde e$)', np.linspace(0, 3, 41)),
        'L_um': (r'$L$ [$\mu$m]', np.linspace(0, 400, 41)),
        'LT_um': (r'$L_T$ [$\mu$m]', np.linspace(0, 150, 41)),
        'e_pT': (r'electron $p_T$ [GeV]', np.linspace(0, 300, 41)),
        'e_eta': (r'electron $\eta$', np.linspace(-5, 5, 41)),
        'jet_pT': (r'truth-jet $p_T$ [GeV]', np.linspace(20, 300, 41)),
        'jet_eta': (r'truth-jet $\eta$', np.linspace(-4.7, 4.7, 41)),
        'n_jets': (r'$N_{\rm jets}$ ($p_T>20$)', np.arange(-0.5, 12.5, 1))}

lines = ['variable,N_zonly,N_gZ,mean_zonly,mean_gZ,KS_D,KS_p']
fig, axs = plt.subplots(3, 3, figsize=(13, 10.5))
for ax, (k, (lab, bins)) in zip(axs.flat, spec.items()):
    a, b = vz[k], vg[k]
    D, pval = ks_2samp(a, b)
    lines.append('%s,%d,%d,%.5g,%.5g,%.4f,%.3g' % (k, len(a), len(b), a.mean(), b.mean(), D, pval))
    ax.hist(b, bins=bins, density=True, histtype='step', lw=1.6, color='#2a78d6', label=r'$\gamma+Z$ (fase 2, 20k ev)')
    ax.hist(a, bins=bins, density=True, histtype='step', lw=1.6, color='#eb6834', label=r'sólo $Z$ (fase 3A, 2k ev)')
    ax.set_xlabel(lab)
    ax.set_title('KS D=%.3f, p=%.2g' % (D, pval), fontsize=9)
axs.flat[0].legend(fontsize=8)
fig.suptitle(r'M = 200 GeV, verdad: sólo-$Z$ vs $\gamma+Z$ (normalizado a área)')
fig.tight_layout()
fig.savefig(os.path.join(out, 'zonly_vs_gZ_M200.png'))
fz = np.mean(vz['LT_um'] > 20)
fg = np.mean(vg['LT_um'] > 20)
nz, ng = len(vz['LT_um']), len(vg['LT_um'])
lines.append('# f(L_T>20um): zonly=%.4f +- %.4f  gZ=%.4f +- %.4f' % (
    fz, np.sqrt(fz * (1 - fz) / nz), fg, np.sqrt(fg * (1 - fg) / ng)))
open(os.path.join(out, 'zonly_vs_gZ_M200_ks.csv'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
