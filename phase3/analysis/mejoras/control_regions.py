#!/usr/bin/env python3
"""Data-driven background for kappa_par: control regions in data (same selection as plot_final.py).
  SR      : OS electrons, chi2 < 6                      (signal region, = Fig. 2)
  SS      : same-sign electrons, chi2 < 6               (no signal: LW pair is OS)
  SB-OS   : OS, chi2 in [6, CHI2HI)                     (mass sideband: m_jj / m_ejj away from 91 / 200)
  SB-SS   : SS, chi2 in [6, CHI2HI)
Vertex quality, L_T > 0.02 mm and kappa definition identical to plot_final.py.
Signal MC is passed through every region to measure contamination.
Usage: ../.venv/bin/python control_regions.py
"""
import glob, os, json
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out_data'); PL = os.path.join(HERE, 'plots_cr'); os.makedirs(PL, exist_ok=True)
MZ, M, SJJ, SEJJ, CHI2MAX = 91.19, 200.0, 15.9, 16.9, 6.0
CHI2HI = [30.0, 100.0, 1e99]

def load(s):
    dn = os.path.join(HERE, 'done_final', s + '.txt')
    done = set(l.strip() for l in open(dn)) if os.path.exists(dn) else set()
    fs = [f for f in sorted(glob.glob(os.path.join(OUT, s, '*.root'))) if os.path.basename(f)[:-5] in done]
    evs = []
    for f in fs:
        evs += ak.to_list(uproot.open(f)['wdv3/events'].arrays(filter_name=['isOS', 'genW', 'pvx', 'pvy', 'e_*', 'c_*', 'f_*']))
    return evs

def chi(e, i): return ((e['c_mjj'][i] - MZ) / SJJ) ** 2 + ((e['c_mejj'][i] - M) / SEJJ) ** 2

def svs(e):
    """same jet assignment as plot_final.select, but returns every chosen candidate with its chi2 (no chi2 cut)"""
    c0 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 0]
    c1 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 1]
    best, bc = None, 1e99
    for i in c0:
        for j in c1:
            if {e['c_j1'][i], e['c_j2'][i]} & {e['c_j1'][j], e['c_j2'][j]}: continue
            c = chi(e, i) + chi(e, j)
            if c < bc: bc, best = c, (i, j)
    if best is None:
        best = tuple(sorted(c0 + c1, key=lambda i: chi(e, i))[:1])
    out = []
    for ci in best:
        js = [j for j in range(len(e['f_cand'])) if e['f_cand'][j] == ci and e['f_clean'][j] == 0 and e['f_fitter'][j] == 2]
        js = [j for j in js if e['f_hasEle'][j] == 1 and e['f_chi2'][j] < 5 and e['f_ntrk'][j] >= 3]
        if not js: continue
        j = js[0]
        dx, dy = e['f_x'][j] - e['pvx'], e['f_y'][j] - e['pvy']
        out.append(dict(k=10 * (dx * e['f_ptx'][j] + dy * e['f_pty'][j]), LT=10 * np.hypot(dx, dy), chi2=chi(e, ci),
                        mjj=e['c_mjj'][ci], mejj=e['c_mejj'][ci], os=e['isOS'] == 1, w=e['genW']))
    return out

def region(rows, os_, lo, hi):
    r = [x for x in rows if x['os'] == os_ and lo <= x['chi2'] < hi and x['LT'] > 0.02]
    return np.array([x['k'] for x in r]), r

def fneg(k):
    n = len(k)
    if n == 0: return None
    f = float((k < 0).mean()); return [f, float(np.sqrt(f * (1 - f) / n)), n]

ROWS = {}
for s in ['data', 'sig_causal', 'sig_acausal', 'DY', 'TT']:
    ROWS[s] = [x for e in load(s) for x in svs(e)]
    print(s, len(ROWS[s]), 'candidate SVs')

res = {}
for s in ROWS:
    d = {'SR': fneg(region(ROWS[s], True, 0, CHI2MAX)[0]), 'SS': fneg(region(ROWS[s], False, 0, CHI2MAX)[0])}
    for hi in CHI2HI:
        t = '%g' % hi if hi < 1e90 else 'inf'
        d['SB-OS_6-' + t] = fneg(region(ROWS[s], True, CHI2MAX, hi)[0])
        d['SB-SS_6-' + t] = fneg(region(ROWS[s], False, CHI2MAX, hi)[0])
        kk = np.concatenate([region(ROWS[s], True, CHI2MAX, hi)[0], region(ROWS[s], False, CHI2MAX, hi)[0]])
        d['SB-all_6-' + t] = fneg(kk)
    res[s] = d
# combined background estimate from data: SS + SB(6-100, OS+SS)
kcomb = np.concatenate([region(ROWS['data'], False, 0, CHI2MAX)[0], region(ROWS['data'], True, CHI2MAX, 100)[0],
                        region(ROWS['data'], False, CHI2MAX, 100)[0]])
res['data']['CR_combined(SS+SB6-100)'] = fneg(kcomb)

# kinematic comparison data SR vs sideband: |kappa| and L_T medians
def med(rows, os_, lo, hi, key):
    r = region(rows, os_, lo, hi)[1]
    return float(np.median([abs(x[key]) for x in r])) if r else None
res['shape_check_data'] = {reg: dict(median_abs_kappa=med(ROWS['data'], o, lo, hi, 'k'), median_LT_mm=med(ROWS['data'], o, lo, hi, 'LT'))
                           for reg, (o, lo, hi) in {'SR': (True, 0, 6), 'SS': (False, 0, 6), 'SB-OS_6-100': (True, 6, 100)}.items()}
def ks(a, b):
    x = np.sort(np.concatenate([a, b])); d = np.abs(np.searchsorted(np.sort(a), x, 'right') / len(a) - np.searchsorted(np.sort(b), x, 'right') / len(b)).max()
    ne = len(a) * len(b) / (len(a) + len(b)); lam = (np.sqrt(ne) + 0.12 + 0.11 / np.sqrt(ne)) * d
    p = 2 * sum((-1) ** (j - 1) * np.exp(-2 * j * j * lam * lam) for j in range(1, 101))
    return [float(d), float(min(max(p, 0), 1))]
ksr0 = region(ROWS['data'], True, 0, CHI2MAX)[0]
res['KS_data_SR_vs_CRcombined'] = dict(kappa=ks(ksr0, kcomb), abs_kappa=ks(np.abs(ksr0), np.abs(kcomb)))
json.dump(res, open(os.path.join(PL, 'numbers_cr.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))

# figure 1: kappa shapes, data SR vs control regions (unit area)
B = np.linspace(-5, 5, 21); c = 0.5 * (B[1:] + B[:-1])
def H(k): return np.histogram(np.clip(k, B[0] + 1e-6, B[-1] - 1e-6), B)[0].astype(float)
fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.2))
ksr = region(ROWS['data'], True, 0, CHI2MAX)[0]
hsr = H(ksr)
ax.errorbar(c, hsr / hsr.sum(), yerr=np.sqrt(hsr) / hsr.sum(), fmt='o', color='k', label='Datos, región de señal (OS, χ²<6): N=%d' % len(ksr))
hc = H(kcomb)
ax.step(B, np.append(hc / hc.sum(), (hc / hc.sum())[-1]), where='post', color='#2457A6', lw=2, label='Datos, regiones de control combinadas: N=%d' % len(kcomb))
ax.fill_between(B, np.append((hc - np.sqrt(hc)) / hc.sum(), ((hc - np.sqrt(hc)) / hc.sum())[-1]),
                np.append((hc + np.sqrt(hc)) / hc.sum(), ((hc + np.sqrt(hc)) / hc.sum())[-1]), step='post', color='#2457A6', alpha=0.2)
ax.axvline(0, color='#888', lw=0.8, ls='--')
ax.set_xlabel(r'$\kappa_\parallel$ (mm·GeV)'); ax.set_ylabel('fracción de vértices / bin'); ax.legend(fontsize=8.5, frameon=False, loc='upper right')
ax.set_title(r'Forma de $\kappa_\parallel$ (L$_T$ > 0.02 mm, área = 1; bins extremos incluyen desbordes)', fontsize=10)
# figure 1b: f(kappa<0) by region
labs, vals, errs, cols = [], [], [], []
for lab, key, s, col in [('Datos: región de señal', 'SR', 'data', 'k'), ('Datos: mismo signo', 'SS', 'data', '#2457A6'),
                         ('Datos: fuera de masa OS', 'SB-OS_6-100', 'data', '#2457A6'), ('Datos: fuera de masa SS', 'SB-SS_6-100', 'data', '#2457A6'),
                         ('Datos: control combinado', 'CR_combined(SS+SB6-100)', 'data', '#2457A6'),
                         ('Señal causal (reflejada)', None, 'sig_causal', '#C8641E'), ('Señal acausal', 'SR', 'sig_acausal', '#1b9e77')]:
    v = res[s][key] if key else None
    if s == 'sig_causal':
        k = region(ROWS[s], True, 0, CHI2MAX)[0]; v = fneg(-k)
    if v is None: continue
    labs.append('%s (N=%d)' % (lab, v[2])); vals.append(v[0]); errs.append(v[1]); cols.append(col)
y = np.arange(len(labs))[::-1]
for v_, y_, e_, c_ in zip(vals, y, errs, cols): bx.errorbar([v_], [y_], xerr=[e_], fmt='o', color=c_, elinewidth=2, capsize=4)
bx.axvline(0.5, color='#888', ls='--', lw=0.8); bx.set_yticks(y); bx.set_yticklabels(labs, fontsize=9)
bx.set_xlim(0.0, 1.0); bx.set_xlabel(r'fracción con $\kappa_\parallel$ < 0')
bx.set_title('¿El fondo da 0.5?', fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(PL, 'cr_kappa.png'), dpi=150); fig.savefig(os.path.join(PL, 'cr_kappa.pdf')); plt.close(fig)
print('saved', PL)
