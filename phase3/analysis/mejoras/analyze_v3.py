#!/usr/bin/env python3
"""Improvements study (signal only): evaluates variants V0..V4 offline on the WDVv3Analyzer ntuples.
Outputs: plots/summary.md, plots/summary.json, plots/fneg_variants.png, plots/kappa_best.png
Usage: ../.venv/bin/python analyze_v3.py
"""
import glob, os, json, itertools
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PL = os.path.join(HERE, 'plots'); os.makedirs(PL, exist_ok=True)
NGEN = {}
MZ, M = 91.19, 200.0
DTRUE = 0.0030   # cm = 30 um: truth-correct definition B (transverse distance to the true decay point)

def load(v):
    fs = sorted(glob.glob(os.path.join(HERE, 'out', v, '*.root')))
    arr, n = [], 0
    for f in fs:
        r = uproot.open(f)
        n += int(r['wdv3/cutflow'].values()[0]); arr.append(r['wdv3/events'].arrays())
    NGEN[v] = n
    return ak.to_list(ak.concatenate(arr))

EV = {v: load(v) for v in ['causal', 'acausal']}

# ---------- mass resolutions from truth-matched candidates (both samples, cleaning-independent)
mjj_t, mejj_t = [], []
for v in EV:
    for e in EV[v]:
        if not e['isOS']: continue
        for i, t in enumerate(e['c_truth']):
            if t == 1: mjj_t.append(e['c_mjj'][i]); mejj_t.append(e['c_mejj'][i])
mjj_t, mejj_t = np.array(mjj_t), np.array(mejj_t)
def robust(x):
    q1, q2, q3 = np.percentile(x, [25, 50, 75]); return float(q2), float((q3 - q1) / 1.349)
MJJ0, SJJ = robust(mjj_t); MEJJ0, SEJJ = robust(mejj_t)
# the chi2 uses the nominal masses (m_Z, M) and the truth widths (peak positions are reported too)

def fits_of(e, ci, clean, fitter):
    out = []
    for j in range(len(e['f_cand'])):
        if e['f_cand'][j] == ci and e['f_clean'][j] == clean and e['f_fitter'][j] == fitter: out.append(j)
    return out

def good_fit(e, j):
    if e['f_fitter'][j] == 0:
        return e['f_hasEle'][j] == 1 and e['f_t21'][j] == 31
    return e['f_hasEle'][j] == 1 and e['f_chi2'][j] < 5 and e['f_ntrk'][j] >= 3

def sv_info(e, j, ci, kobj=False):
    x, y = e['f_x'][j], e['f_y'][j]
    dx, dy = x - e['pvx'], y - e['pvy']
    if kobj: px, py = e['c_px'][ci], e['c_py'][ci]
    else: px, py = e['f_ptx'][j], e['f_pty'][j]
    kap = 10 * (dx * px + dy * py)
    LT = np.hypot(dx, dy)
    cxx, cxy, cyy = e['f_cxx'][j] + e['pvcxx'], e['f_cxy'][j] + e['pvcxy'], e['f_cyy'][j] + e['pvcyy']
    sLT = np.sqrt(max(0., dx * dx * cxx + 2 * dx * dy * cxy + dy * dy * cyy)) / LT if LT > 0 else 0
    k = e['c_ele'][ci]; lw = e['e_lw'][k]
    dT = tL = None
    if lw >= 0 and lw < len(e['t_dvx']):
        dT = float(np.hypot(x - e['t_dvx'][lw], y - e['t_dvy'][lw]))
        tL = float(np.hypot(e['t_dvx'][lw] - e['t_pvx'][lw], e['t_dvy'][lw] - e['t_pvy'][lw]))
    return dict(k=kap, LT=10 * LT, LTsig=LT / sLT if sLT > 0 else 0, truthA=e['c_truth'][ci] == 1,
                truthB=(dT is not None and dT < DTRUE), dT=None if dT is None else 10 * dT, tL=None if tL is None else 10 * tL,
                ptejj=e['c_ptejj'][ci], ept=e['e_pt'][k])

def assign(e, chi2max=None):
    """best disjoint jet-pair assignment to the two electrons (chi2 of m_jj and m_ejj)."""
    c0 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 0]
    c1 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 1]
    def chi(i): return ((e['c_mjj'][i] - MZ) / SJJ) ** 2 + ((e['c_mejj'][i] - M) / SEJJ) ** 2
    best, bc = None, 1e99
    for i in c0:
        for j in c1:
            if {e['c_j1'][i], e['c_j2'][i]} & {e['c_j1'][j], e['c_j2'][j]}: continue
            c = chi(i) + chi(j)
            if c < bc: bc, best = c, (i, j)
    if best is None:   # only one electron has candidates
        cands = sorted(c0 + c1, key=chi)
        if not cands: return []
        best = (cands[0],); bc = chi(cands[0])
    out = list(best)
    if chi2max is not None: out = [i for i in out if chi(i) < chi2max]
    return out

def variant(name, sample, mode, clean=0, fitter=0, both=False, chi2max=None, LTmin=None, LTsig=None, ptmin=None, eptmin=None, kobj=False):
    sel = []; nev = 0
    for e in EV[sample]:
        if not e['isOS']: continue
        rows = []
        if mode in ('V0', "V0'"):
            if mode == 'V0' and not any(e['e_drc']): continue
            for ci in range(len(e['c_ele'])):
                if not (80 < e['c_mjj'][ci] < 160): continue
                for j in fits_of(e, ci, clean, fitter):
                    if good_fit(e, j): rows.append(sv_info(e, j, ci, kobj))
            if LTmin is None: LTmin = 0.02
        else:
            per_e = {}
            for ci in assign(e, chi2max):
                js = [j for j in fits_of(e, ci, clean, fitter) if good_fit(e, j)]
                if js:   # one SV per electron: rank 0 (SVRA: most tracks), single fit otherwise
                    per_e[e['c_ele'][ci]] = sv_info(e, js[0], ci, kobj)
            if both and len(per_e) < 2: continue
            rows = list(per_e.values())
        if LTmin is not None: rows = [r for r in rows if r['LT'] > LTmin]
        if LTsig is not None: rows = [r for r in rows if r['LTsig'] > LTsig]
        if ptmin is not None: rows = [r for r in rows if r['ptejj'] > ptmin]
        if eptmin is not None: rows = [r for r in rows if r['ept'] > eptmin]
        if both and mode not in ('V0', "V0'") and len(rows) < 2: continue
        if rows: nev += 1; sel += rows
    return nev, sel

def binom(k, n): return (k / n, np.sqrt(k / n * (1 - k / n) / n)) if n else (np.nan, np.nan)

def metrics(nev, rows, sample):
    n = len(rows)
    eff = binom(nev, NGEN[sample])
    kk = np.array([r['k'] for r in rows])
    fneg = binom(float((kk < 0).sum()), n)
    fa = binom(float(sum(r['truthA'] for r in rows)), n)
    fb = binom(float(sum(r['truthB'] for r in rows)), n)
    dT = [r['dT'] for r in rows if r['dT'] is not None]; tL = [r['tL'] for r in rows if r['tL'] is not None]
    ka = np.array([r['k'] for r in rows if r['truthA']])
    return dict(nev=nev, nsv=n, eff=eff, fneg=fneg, fA=fa, fB=fb, fnegA=binom(float((ka < 0).sum()), len(ka)),
                med_dT_um=float(np.median(dT) * 1000) if dT else None, med_trueLT_um=float(np.median(tL) * 1000) if tL else None)

VARS = [
    ('V0 (v2: SVRA, DRC, 80<mjj<160, L_T>0.02)', dict(mode='V0')),
    ("V0' (V0 sin DRC)", dict(mode="V0'")),
    ('V1 asignación χ², SVRA', dict(mode='V1', fitter=0)),
    ('V1 asignación χ², KVF todas', dict(mode='V1', fitter=1)),
    ('V1 asignación χ², AVF todas', dict(mode='V1', fitter=2)),
    ('V1 AVF + χ²<6 por electrón', dict(mode='V1', fitter=2, chi2max=6)),
    ('V2 = V1 AVF + ambos e con SV', dict(mode='V1', fitter=2, both=True)),
    ('V3 V1 AVF, limpieza c1 (sin trazas del PV/PU)', dict(mode='V1', fitter=2, clean=1)),
    ('V3 V1 AVF, limpieza c2 (PU + IPsig<2)', dict(mode='V1', fitter=2, clean=2)),
    ('V3 V1 AVF, limpieza c3 (PU + IPsig<3)', dict(mode='V1', fitter=2, clean=3)),
    ('V3 V1 SVRA, limpieza c2', dict(mode='V1', fitter=0, clean=2)),
    ('V3 V1 KVF, limpieza c2', dict(mode='V1', fitter=1, clean=2)),
]
BEST3 = dict(mode='V1', fitter=2, clean=2)
for lab, extra in [('L_T/σ>2', dict(LTsig=2)), ('L_T/σ>3', dict(LTsig=3)), ('pT(ejj)>100', dict(ptmin=100)),
                   ('pT(ejj)>150', dict(ptmin=150)), ('pT(ejj)>200', dict(ptmin=200)), ('pT(e)>100', dict(eptmin=100)),
                   ('L_T/σ>2 + pT(ejj)>150', dict(LTsig=2, ptmin=150)), ('L_T/σ>3 + pT(ejj)>150', dict(LTsig=3, ptmin=150))]:
    d = dict(BEST3); d.update(extra); VARS.append(('V4 V3(AVF,c2) + ' + lab, d))
for lab, extra in [('L_T/σ>2', dict(LTsig=2)), ('L_T/σ>3', dict(LTsig=3)), ('pT(ejj)>150', dict(ptmin=150))]:
    d = dict(mode='V1', fitter=2, clean=0); d.update(extra); VARS.append(('V4 V1(AVF,c0) + ' + lab, d))

res = []
for lab, kw in VARS:
    r = {'variant': lab}
    for s in ['causal', 'acausal']:
        nev, rows = variant(lab, s, **kw); r[s] = metrics(nev, rows, s)
        if lab.startswith('V4 V3(AVF,c2) + L_T/σ>2 +') or lab == 'V2 = V1 AVF + ambos e con SV': pass
        r[s + '_k'] = [x['k'] for x in rows]
    fc, ec = r['causal']['fneg']; fa, ea = r['acausal']['fneg']
    r['sep_sigma'] = float((fa - fc) / np.hypot(ec, ea)) if ec and ea and ec > 0 else None
    res.append(r)

def f(x, p=2):
    return '-' if x is None or (isinstance(x, float) and np.isnan(x)) else ('%.*f' % (p, x))
L = ['# Estudio de mejoras (solo señal, M = 200 GeV sólo-Z, 500 causales + 500 acausales)', '',
     'Resoluciones de masa (candidatos con verdad correcta): m_jj pico %.1f GeV, σ_jj = %.1f GeV; m_ejj pico %.1f GeV, σ_ejj = %.1f GeV '
     '(mediana y IQR/1.349). χ² = ((m_jj−m_Z)/σ_jj)² + ((m_ejj−200)/σ_ejj)², usando la hipótesis de masa M = 200 GeV.' % (MJJ0, SJJ, MEJJ0, SEJJ), '',
     'Definiciones: ef = eventos con ≥1 SV seleccionado / 500; verdad A = electrón hijo del ℓ̃ y ambos jets emparejados (ΔR<0.4) a los quarks del Z del MISMO ℓ̃; '
     'verdad B = |SV − vértice de desintegración verdadero|_T < 30 µm; f(κ<0) con κ∥ = (PV→SV)_T·P_T(trazas); sep = (f_acausal − f_causal)/σ. '
     'Δ_T = mediana |SV_reco − SV_verdadero|_T; L_T verdadera = mediana de la distancia transversal verdadera PV→SV.', '',
     '| variante | ef causal | ef acausal | N SV c/a | verdad A c/a | verdad B c/a | f(κ<0) causal | f(κ<0) acausal | sep (σ) | f(κ<0) verdad A c/a | Δ_T (µm) c/a | L_T verdadera (µm) c/a |',
     '|' + '---|' * 12]
for r in res:
    c, a = r['causal'], r['acausal']
    L.append('| %s | %s±%s | %s±%s | %d/%d | %s/%s | %s/%s | %s±%s | %s±%s | %s | %s/%s | %s/%s | %s/%s |' % (
        r['variant'], f(c['eff'][0]), f(c['eff'][1]), f(a['eff'][0]), f(a['eff'][1]), c['nsv'], a['nsv'],
        f(c['fA'][0]), f(a['fA'][0]), f(c['fB'][0]), f(a['fB'][0]), f(c['fneg'][0]), f(c['fneg'][1]), f(a['fneg'][0]), f(a['fneg'][1]),
        f(r['sep_sigma'], 1), f(c['fnegA'][0]), f(a['fnegA'][0]), f(c['med_dT_um'], 0), f(a['med_dT_um'], 0), f(c['med_trueLT_um'], 0), f(a['med_trueLT_um'], 0)))
open(os.path.join(PL, 'summary.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
json.dump(dict(masses=dict(mjj_peak=MJJ0, sjj=SJJ, mejj_peak=MEJJ0, sejj=SEJJ, n_truth=len(mjj_t)), NGEN=NGEN,
               variants=[{k: v for k, v in r.items() if not k.endswith('_k')} for r in res]),
          open(os.path.join(PL, 'summary.json'), 'w'), indent=1)

# ---------- plots
fig, ax = plt.subplots(figsize=(8, 6.5))
y = np.arange(len(res))[::-1]
for r, yy in zip(res, y):
    ax.errorbar(r['causal']['fneg'][0], yy + 0.12, xerr=r['causal']['fneg'][1], fmt='o', color='#1b9e77', ms=4)
    ax.errorbar(r['acausal']['fneg'][0], yy - 0.12, xerr=r['acausal']['fneg'][1], fmt='s', color='#7570b3', ms=4)
ax.axvline(0.5, color='k', lw=0.8, ls='--')
ax.set_yticks(y); ax.set_yticklabels([r['variant'] for r in res], fontsize=7)
ax.set_xlabel(r'$f(\kappa_\parallel<0)$'); ax.set_xlim(0, 1)
ax.plot([], [], 'o', color='#1b9e77', label='causal'); ax.plot([], [], 's', color='#7570b3', label='acausal (reflejado)')
ax.legend(fontsize=8, loc='lower right'); ax.set_title('Fracción de SV con κ∥<0 por variante (señal M=200)', fontsize=9)
fig.savefig(os.path.join(PL, 'fneg_variants.png'), dpi=150, bbox_inches='tight'); fig.savefig(os.path.join(PL, 'fneg_variants.pdf'), bbox_inches='tight')
plt.close(fig)
# best variant = largest separation with >= 50 SVs per sample
cands = [r for r in res if r['causal']['nsv'] >= 50 and r['acausal']['nsv'] >= 50 and r['sep_sigma'] is not None]
best = max(cands, key=lambda r: r['sep_sigma'])
for rr, tag in [(best, 'best'), (res[0], 'V0')]:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    b = np.linspace(-30, 30, 31)
    for s, col, ls in [('causal', '#1b9e77', '-'), ('acausal', '#7570b3', '--')]:
        k = np.clip(np.array(rr[s + '_k']), -29.99, 29.99)
        h = np.histogram(k, b)[0]
        ax.step(b, np.append(h, h[-1]), where='post', color=col, ls=ls, lw=1.8,
                label='%s: N=%d, f(κ<0)=%.2f±%.2f' % (s, len(k), rr[s]['fneg'][0], rr[s]['fneg'][1]))
    ax.axvline(0, color='k', lw=0.6)
    ax.set_xlabel(r'$\kappa_\parallel$ (mm$\cdot$GeV)'); ax.set_ylabel('SV / 2 mm·GeV')
    ax.set_title(rr['variant'] + ' (sep = %.1fσ)' % rr['sep_sigma'], fontsize=8); ax.legend(fontsize=8, frameon=False)
    fig.savefig(os.path.join(PL, 'kappa_%s.png' % tag), dpi=150, bbox_inches='tight'); fig.savefig(os.path.join(PL, 'kappa_%s.pdf' % tag), bbox_inches='tight')
    plt.close(fig)
# mass distributions of truth-matched candidates
fig, axs = plt.subplots(1, 2, figsize=(9, 3.5))
axs[0].hist(mjj_t, np.linspace(40, 180, 36)); axs[0].set_xlabel('m_jj (GeV), verdad A'); axs[0].axvline(MZ, color='r')
axs[1].hist(mejj_t, np.linspace(80, 360, 36)); axs[1].set_xlabel('m_ejj (GeV), verdad A'); axs[1].axvline(M, color='r')
fig.savefig(os.path.join(PL, 'masses_truth.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
print('best:', best['variant'], best['sep_sigma'])
