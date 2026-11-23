#!/usr/bin/env python3
"""lwrep_check.py -- parton-level (LHE) comparison of lwRep = 0 (Eq. 1 literal, default) vs lwRep = 1
(vector-like partner: elw_R couples to Z like e_L) at M = 200 GeV.

Observables: cos(theta*) of elw- in the pair rest frame (z = beam), pT and beta*gamma(_T) of elw,
helicity angle of the e- in the elw- rest frame (w.r.t. the elw- flight direction; polarisation
sensitive), pT and |eta| of the electrons, and the Z->qq angle.  Cross sections are read from the
banners.  Output: plots/lwrep_comparison_M200.png and a printed table.
"""
import gzip
import os
import re

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), 'mg5', 'PROC_lw_ejj', 'Events')


def boost_to(v, P):
    """boost 4-vector v into the rest frame of P"""
    b = P[:3] / P[3]
    b2 = b @ b
    g = 1 / np.sqrt(1 - b2)
    bp = b @ v[:3]
    sp = v[:3] + ((g - 1) / b2 * bp - g * v[3]) * b
    return np.array([*sp, g * (v[3] - bp)])


def read(run, M=200.):
    path = os.path.join(EV, run, 'unweighted_events.lhe.gz')
    rows = []
    with gzip.open(path, 'rt') as f:
        ev = None
        for l in f:
            if l.startswith('<event'):
                ev = []
            elif l.startswith('</event'):
                parts = [x.split() for x in ev[1:] if x.strip() and not x.startswith('#') and not x.startswith('<')]
                ids = [int(x[0]) for x in parts]
                mo = [int(x[2]) for x in parts]
                p = [np.array([float(v) for v in x[6:10]]) for x in parts]
                iwm, iwp = ids.index(9000011), ids.index(-9000011)
                iem = [i for i in range(len(ids)) if ids[i] == 11 and mo[i] == iwm + 1][0]
                iep = [i for i in range(len(ids)) if ids[i] == -11 and mo[i] == iwp + 1][0]
                izm = [i for i in range(len(ids)) if ids[i] == 23 and mo[i] == iwm + 1][0]
                qz = [i for i in range(len(ids)) if mo[i] == izm + 1]
                wm, wp = p[iwm], p[iwp]
                pair = wm + wp
                w_cm = boost_to(wm, pair)
                cth = w_cm[2] / np.linalg.norm(w_cm[:3])
                e_r = boost_to(p[iem], wm)
                w_dir = wm[:3] / np.linalg.norm(wm[:3])
                chel = e_r[:3] @ w_dir / np.linalg.norm(e_r[:3])
                # Z -> q q angle in Z rest frame w.r.t. Z direction (in elw rest frame)
                z_r = boost_to(p[izm], wm)
                q_z = boost_to(boost_to(p[qz[0]], wm), z_r)
                cq = q_z[:3] @ z_r[:3] / np.linalg.norm(q_z[:3]) / np.linalg.norm(z_r[:3])
                for w in (wm, wp):
                    pass
                rows.append((cth, np.hypot(*wm[:2]), np.linalg.norm(wm[:3]) / M, np.hypot(*wm[:2]) / M,
                             chel, np.hypot(*p[iem][:2]), np.hypot(*p[iep][:2]),
                             abs(0.5 * np.log((np.linalg.norm(p[iem][:3]) + p[iem][2]) /
                                              (np.linalg.norm(p[iem][:3]) - p[iem][2]))), abs(cq)))
                ev = None
            elif ev is not None:
                ev.append(l)
    ban = open(os.path.join(EV, run, '%s_tag_1_banner.txt' % run)).read()
    xs = float(re.search(r'Integrated weight \(pb\)\s*:\s*([0-9.eE+-]+)', ban).group(1))
    return np.array(rows), xs


def main():
    names = ['cos theta* (elw-)', 'pT(elw-) [GeV]', 'beta*gamma', 'beta*gamma_T', 'cos theta_hel (e- in elw-)',
             'pT(e-) [GeV]', 'pT(e+) [GeV]', '|eta(e-)|', '|cos theta_q| (Z rest)']
    rng = [(-1, 1), (0, 500), (0, 5), (0, 3), (-1, 1), (0, 400), (0, 400), (0, 4), (0, 1)]
    A, xa = read('M200')
    B, xb = read('M200_lwRep1')
    print('sigma x BR(Z->had)^2 : lwRep=0 %.5g pb, lwRep=1 %.5g pb, ratio %.3f' % (xa, xb, xb / xa))
    print('%-28s %10s %10s %8s' % ('observable', 'lwRep=0', 'lwRep=1', 'KS D'))
    fig, ax = plt.subplots(3, 3, figsize=(12, 9))
    for i, n in enumerate(names):
        a, b = A[:, i], B[:, i]
        grid = np.sort(np.concatenate([a, b]))
        ks = np.max(np.abs(np.searchsorted(np.sort(a), grid, 'right') / len(a) -
                           np.searchsorted(np.sort(b), grid, 'right') / len(b)))
        print('%-28s %10.4f %10.4f %8.4f' % ('<' + n + '>', a.mean(), b.mean(), ks))
        x = ax.flat[i]
        x.hist(a, bins=40, range=rng[i], histtype='step', density=True, lw=1.6, color='#2a78d6', label='lwRep=0 (default)')
        x.hist(b, bins=40, range=rng[i], histtype='step', density=True, lw=1.6, color='#eb6834', label='lwRep=1')
        x.set_xlabel(n)
        x.set_title('KS D = %.3f (N=%d, %d)' % (ks, len(a), len(b)), fontsize=8)
        x.legend(fontsize=7, frameon=False)
    fig.suptitle('M=200 GeV, parton level (LHE): lwRep=0 vs 1;  sigma ratio = %.3f' % (xb / xa), fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.join(HERE, 'plots'), exist_ok=True)
    fig.savefig(os.path.join(HERE, 'plots', 'lwrep_comparison_M200.png'))
    LT0 = A[:, 3].mean() * 27.0765
    LT1 = B[:, 3].mean() * 27.0765
    print('implied <L_T> = <bgT> ctau0 : %.2f um (lwRep=0)  %.2f um (lwRep=1)' % (LT0, LT1))


if __name__ == '__main__':
    main()
