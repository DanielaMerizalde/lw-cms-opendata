#!/usr/bin/env python3
"""summarize_verify.py CAUSAL.csv ACAUSAL.csv TRUTH_elw.csv OUTPREFIX
Summarise the per-LW rows written by verify_edm.py (causal and acausal versions of the same events):
 (a) GEN : (SV-PV) after MCFileSource+VtxSmeared vs HepMC truth (causal: +d, acausal: -d), and PV_causal == PV_acausal
 (b) G4  : SimVertex of the electron SimTrack vs SV
 (c) RECO: electron track d_xy (w.r.t. true PV / reco PV) vs the true d_xy; sign test and paired causal-acausal slope.
"""
import csv
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

cf, af, tf, out = sys.argv[1:5]
C = {(int(r['iev']), int(r['pdg'])): r for r in csv.DictReader(open(cf))}
A = {(int(r['iev']), int(r['pdg'])): r for r in csv.DictReader(open(af))}
T = {(int(r['iev']), int(r['id'])): r for r in csv.DictReader(open(tf))}
keys = sorted(set(C) & set(A))


def g(r, k):
    v = r.get(k, '')
    return float(v) if v not in ('', None) else np.nan


L = []
for k in keys:
    c, a, t = C[k], A[k], T[k]
    d0 = np.array([float(t['xd']) - float(t['xp']), float(t['yd']) - float(t['yp']), float(t['zd']) - float(t['zp'])])  # mm
    dc = 10 * np.array([g(c, 'SV' + x) - g(c, 'PV' + x) for x in 'xyz'])
    da = 10 * np.array([g(a, 'SV' + x) - g(a, 'PV' + x) for x in 'xyz'])
    pvd = 1e4 * np.max(np.abs([g(c, 'PV' + x) - g(a, 'PV' + x) for x in 'xyz']))
    L.append(dict(gen_c=np.max(np.abs(dc - d0)), gen_a=np.max(np.abs(da + d0)), pvd=pvd,
                  g4_c=g(c, 'g4_minus_SV_um'), g4_a=g(a, 'g4_minus_SV_um'),
                  LT=1e3 * np.hypot(d0[0], d0[1]), dxy_t=g(c, 'dxy_true_PV_um'), dxy_ta=g(a, 'dxy_true_PV_um'),
                  pt=g(c, 'e_pt'), eta=g(c, 'e_eta'),
                  tc=g(c, 'trk_dxy_truePV_um'), ta=g(a, 'trk_dxy_truePV_um'),
                  rc=g(c, 'trk_dxy_recoPV_um'), ra=g(a, 'trk_dxy_recoPV_um'),
                  ec=g(c, 'trk_dxyErr_um'), npix=g(c, 'trk_nPixHits')))
D = {k: np.array([x[k] for x in L]) for k in L[0]}
lines = []
p = lines.append
p('N LW decays (both versions): %d' % len(L))
p('(a) GEN  max|(SV-PV)_gen - d_HepMC|  causal = %.2e mm, acausal (vs -d) = %.2e mm' % (np.nanmax(D['gen_c']), np.nanmax(D['gen_a'])))
p('    max |PV_causal - PV_acausal| = %.3g um (common random numbers in VtxSmeared)' % np.nanmax(D['pvd']))
p('    dxy_true acausal = -causal: max|sum| = %.2e um' % np.nanmax(np.abs(D['dxy_t'] + D['dxy_ta'])))
p('(b) G4   max|SimVertex(e) - SV|  causal = %.3g um, acausal = %.3g um; electrons w/o matched SimTrack: %d/%d' % (
    np.nanmax(D['g4_c']), np.nanmax(D['g4_a']), int(np.sum(np.isnan(D['g4_c'])) + np.sum(np.isnan(D['g4_a']))), 2 * len(L)))
m = ~np.isnan(D['tc']) & ~np.isnan(D['ta']) & (D['npix'] >= 1)
p('(c) RECO electrons with generalTrack match (dR<0.05) in both versions: %d / %d' % (m.sum(), len(L)))
if m.sum() > 2:
    s = np.sign(D['dxy_t'][m])
    for lab, kc, ka in (('true PV', 'tc', 'ta'), ('reco PV', 'rc', 'ra')):
        xc, xa = D[kc][m], D[ka][m]
        ok = ~np.isnan(xc) & ~np.isnan(xa)
        sc, sa = (s * xc)[ok], (s * xa)[ok]
        half = 0.5 * (xc - xa)[ok]
        t = D['dxy_t'][m][ok]
        slope = np.sum(half * t) / np.sum(t * t)
        corr = np.corrcoef(half, t)[0, 1] if ok.sum() > 2 else np.nan
        p('    dxy w.r.t. %s: <sign(dxy_true)*dxy_reco> causal = %+.1f +- %.1f um, acausal = %+.1f +- %.1f um (expect +<|dxy_true|> = %+.1f / -%.1f)' % (
            lab, np.median(sc), 1.2533 * np.std(sc) / np.sqrt(len(sc)), np.median(sa), 1.2533 * np.std(sa) / np.sqrt(len(sa)),
            np.mean(np.abs(t)), np.mean(np.abs(t))))
        p('       paired (dxy_c - dxy_a)/2 vs dxy_true: slope = %.2f (expect 1), corr = %.2f, N = %d' % (slope, corr, ok.sum()))
    p('    median dxy error = %.1f um; median |dxy_true| = %.1f um' % (np.nanmedian(D['ec'][m]), np.median(np.abs(D['dxy_t'][m]))))
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    ax[0].scatter(D['dxy_t'][m], D['tc'][m], s=6, c='#2a78d6', label='causal')
    ax[0].scatter(D['dxy_ta'][m], D['ta'][m], s=6, c='#eb6834', label='acausal')
    ax[0].set_xlabel(r'true $d_{xy}$ (e, vs true PV) [$\mu$m]'); ax[0].set_ylabel(r'reco track $d_{xy}$ vs true PV [$\mu$m]')
    ax[0].set_xlim(-150, 150); ax[0].set_ylim(-200, 200); ax[0].legend()
    ax[1].scatter(D['tc'][m], D['ta'][m], s=6, c='#555')
    ax[1].set_xlabel(r'causal reco $d_{xy}$ [$\mu$m]'); ax[1].set_ylabel(r'acausal reco $d_{xy}$ [$\mu$m]')
    ax[1].set_xlim(-200, 200); ax[1].set_ylim(-200, 200)
    ax[2].scatter(D['dxy_t'][m], 0.5 * (D['tc'] - D['ta'])[m], s=6, c='#1baf7a')
    ax[2].plot([-150, 150], [-150, 150], 'k--', lw=0.8)
    ax[2].set_xlabel(r'true $d_{xy}$ causal [$\mu$m]'); ax[2].set_ylabel(r'$(d_{xy}^{c}-d_{xy}^{a})/2$ reco [$\mu$m]')
    ax[2].set_xlim(-150, 150); ax[2].set_ylim(-200, 200)
    fig.tight_layout(); fig.savefig(out + '_dxy.png')
open(out + '_summary.txt', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
