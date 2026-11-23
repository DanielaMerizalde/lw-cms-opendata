#!/usr/bin/env python3
"""|cos theta*| of the elw- in the elw+elw- rest frame (w.r.t. the boost axis ~ beam), Z-only vs gamma+Z, M=200.
Explains the beta*gamma_T difference. Usage: costheta_star.py ZONLY_DIR GZ_DIR OUT_DIR"""
import os, sys
import numpy as np
from scipy.stats import ks_2samp
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def cts(d):
    e = np.genfromtxt(os.path.join(d, 'truth_M200_elw.csv'), delimiter=',', names=True)
    e = e[np.argsort(e['iev'] * 10 + (e['id'] > 0))]
    a, b = e[0::2], e[1::2]          # a: elw+ (id<0), b: elw- (id>0)
    assert np.all(a['iev'] == b['iev'])
    P = np.stack([a[k] + b[k] for k in ('px', 'py', 'pz', 'E')], 1)
    p = np.stack([b[k] for k in ('px', 'py', 'pz', 'E')], 1)
    bv = P[:, :3] / P[:, 3:4]; b2 = (bv ** 2).sum(1); g = 1 / np.sqrt(1 - b2)
    bp = (bv * p[:, :3]).sum(1)
    pr = p[:, :3] + ((g - 1) * bp / np.maximum(b2, 1e-30) - g * p[:, 3])[:, None] * bv
    return pr[:, 2] / np.linalg.norm(pr, axis=1), np.sqrt((P[:, 3] ** 2 - (P[:, :3] ** 2).sum(1)))

cz, mz = cts(sys.argv[1]); cg, mg = cts(sys.argv[2])
D, pv = ks_2samp(cz, cg); Dm, pm = ks_2samp(mz, mg)
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
bins = np.linspace(-1, 1, 21)
ax[0].hist(cg, bins, density=True, histtype='step', lw=1.6, color='#2a78d6', label=r'$\gamma+Z$')
ax[0].hist(cz, bins, density=True, histtype='step', lw=1.6, color='#eb6834', label=r'sólo $Z$')
ax[0].set_xlabel(r'$\cos\theta^*(\tilde e^-)$ (sistema $\tilde e\tilde e$, eje z)'); ax[0].legend(); ax[0].set_title('KS D=%.3f p=%.2g' % (D, pv), fontsize=9)
bm = np.linspace(400, 1200, 41)
ax[1].hist(mg, bm, density=True, histtype='step', lw=1.6, color='#2a78d6'); ax[1].hist(mz, bm, density=True, histtype='step', lw=1.6, color='#eb6834')
ax[1].set_xlabel(r'$m(\tilde e^+\tilde e^-)$ [GeV]'); ax[1].set_title('KS D=%.3f p=%.2g' % (Dm, pm), fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(sys.argv[3], 'costheta_mee_zonly_vs_gZ_M200.png'))
print('<cos^2 theta*> zonly=%.4f gZ=%.4f  KS D=%.3f p=%.2g | <m_ee> zonly=%.1f gZ=%.1f KS D=%.3f p=%.2g | <cos theta*> zonly=%.4f gZ=%.4f' % (
    np.mean(cz ** 2), np.mean(cg ** 2), D, pv, mz.mean(), mg.mean(), Dm, pm, cz.mean(), cg.mean()))
