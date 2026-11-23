#!/usr/bin/env python3
"""QCD multijet (fake electrons) estimated from DATA, for the kappa_par analysis (v2 thesis selection).

Inputs: qcd/out/<sample>/*.root from WDVQCDAnalyzer (prod_qcd.py). MC (DY, TT, W1-3: 1 file each) is used
only to subtract the small prompt-electron contamination in the control regions.

Method 1 (main, as in the thesis/paper: QCD from the same-sign region)
    QCD_OS = R * (Data_SS - MC_SS)
  with R = OS/SS measured in the ANTI-ISOLATED region (both electrons e_iso >= ISO_CUT), where QCD dominates:
    R = (Data - MC)_OS,anti / (Data - MC)_SS,anti
  R is measured (a) at level A (tree elA: trigger + 2 electrons, any number of jets) — many events — and
  (b) at the analysis level (tree events: after JetS + DRC), to test that R does not depend on the jets.
  The kappa_par shape of QCD is taken from the SS vertices (L_T > 0.02 mm) with weight R.

Method 2 (cross-check, "tight-to-loose"; only meaningful for a selection that requires TIGHT electrons)
    F = N(tight) / N(loose-not-tight), electrons with ID WITHOUT isolation (idBits & 8) as the loose set,
  measured on level-A SS electrons outside the Z window (fake-dominated), barrel / endcap separately.
  Prediction of fakes in the OS analysis region with both electrons tight:
    N_fake = sum_{1 electron fails tight} F  -  sum_{2 fail} F1*F2

Errors on fractions f(kappa<0) are computed by bootstrapping EVENTS (several vertices of an event are
correlated), not vertices.

Usage:  .venv/bin/python qcd/qcd_desde_datos.py [--indir qcd/out] [--iso 0.15]
Output: qcd/plots/qcd_numeros.json, qcd_resumen.md, kappa_qcd.png, mee_regiones.png
"""
import os, glob, json, argparse
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ANA = os.path.dirname(HERE)
XS = {'DY': 3503.7, 'TT': 225.2, 'W1': 6662.8, 'W2': 2159.2, 'W3': 640.4}   # pb, same as plot_final.py
LT_CUT = 0.02                                                              # mm
BINS = np.arange(-150, 151, 10)
rng = np.random.default_rng(12345)

ap = argparse.ArgumentParser()
ap.add_argument('--indir', default=os.path.join(HERE, 'out'))
ap.add_argument('--iso', type=float, default=0.15)
ap.add_argument('--lumi', type=float, default=None, help='pb^-1 of the processed data (default: qcd/lumi_qcd.json, else ../lumi_processed.json)')
ap.add_argument('--outdir', default=os.path.join(HERE, 'plots'))
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
_lj = os.path.join(HERE, 'lumi_qcd.json')
L = args.lumi or json.load(open(_lj if os.path.exists(_lj) else os.path.join(ANA, 'lumi_processed.json')))['L_processed_pb']

EV_BR = ['isOS', 'isSS', 'genW', 'e_iso', 'e_idBits', 'e_eta', 'sv_k', 'sv_LT']
A_BR = ['isOS', 'genW', 'mee', 'nJetGood', 'passTF', 'e_iso', 'e_idBits', 'e_eta', 'e_pt']

def load(sample):
    fs = sorted(glob.glob(os.path.join(args.indir, sample, '*.root')))
    fs = [f for f in fs if not f.endswith('.tmp.root')]
    if not fs: return None
    ev, A, nw = [], [], 0.
    for f in fs:
        r = uproot.open(f)
        nw += r['wdv/cutflow_os_w'].values()[0]          # sum of gen-weight signs before any cut (NF)
        ev.append(r['wdv/events'].arrays(EV_BR)); A.append(r['wdv/elA'].arrays(A_BR))
    ev = ak.concatenate(ev); A = ak.concatenate(A)
    w = 1. if sample == 'data' else XS[sample] * L / nw
    return dict(ev=ev, A=A, w=w, nfiles=len(fs))

S = {s: load(s) for s in ['data', 'DY', 'TT', 'W1', 'W2', 'W3']}
if S['data'] is None: raise SystemExit('No hay salidas de datos en ' + args.indir)
MC = [s for s in XS if S[s] is not None]
print('L = %.1f pb^-1 ; MC disponible: %s' % (L, MC))

def iso_reg(t, anti):
    """event masks: both electrons isolated (anti=False) or both anti-isolated (anti=True)"""
    i = t['e_iso']
    return ak.all(i >= args.iso, axis=1) if anti else ak.all(i < args.iso, axis=1)

def count(tree, mask, w, sample):
    """weighted yield and its variance (data: w=1; MC: per-event gen sign x normalisation)"""
    if sample == 'data':
        n = float(ak.sum(mask)); return n, n
    g = ak.to_numpy(tree['genW'][mask]) * w
    return float(g.sum()), float((g ** 2).sum())

def data_minus_mc(level, mask_fn):
    d, vd = count(S['data'][level], mask_fn(S['data'][level]), 1., 'data')
    m = vm = 0.
    for s in MC:
        a, b = count(S[s][level], mask_fn(S[s][level]), S[s]['w'], s); m += a; vm += b
    return d - m, vd + vm, d, m

def ratio(a, va, b, vb):
    if b <= 0 or a <= 0: return float('nan'), float('nan')
    r = a / b; return r, r * np.sqrt(va / a ** 2 + vb / b ** 2)

res = dict(L_pb=L, iso_cut=args.iso, mc=MC)

# ---------------- R = OS/SS in the anti-isolated region
R = {}
defs = {
    'A_todos':  ('A', lambda t: True),
    'A_nj>=1':  ('A', lambda t: t['nJetGood'] >= 1),
    'A_nj>=2':  ('A', lambda t: t['nJetGood'] >= 2),
    'A_nj>=4':  ('A', lambda t: t['nJetGood'] >= 4),
    'analisis': ('ev', lambda t: True),            # after JetS + DRC (thesis selection)
}
for name, (lev, extra) in defs.items():
    os_ = data_minus_mc(lev, lambda t: (t['isOS'] == 1) & iso_reg(t, True) & extra(t))
    ss_ = data_minus_mc(lev, lambda t: (t['isOS'] == 0) & iso_reg(t, True) & extra(t))
    r, er = ratio(os_[0], os_[1], ss_[0], ss_[1])
    R[name] = dict(R=r, err=er, OS_datos=os_[2], OS_mc=os_[3], SS_datos=ss_[2], SS_mc=ss_[3])
    print('R(%-9s) = %.3f +- %.3f   [anti-iso: OS datos %d (MC %.1f), SS datos %d (MC %.1f)]' % (
        name, r, er, os_[2], os_[3], ss_[2], ss_[3]))
res['R'] = R
# R used: analysis level if it has a meaningful error (< 30 %), otherwise level A (all events)
Ruse = R['analisis'] if np.isfinite(R['analisis']['err']) and R['analisis']['err'] < 0.3 * R['analisis']['R'] else R['A_todos']
if not np.isfinite(Ruse['R']): Ruse = dict(R=1.0, err=0.5)
res['R_usado'] = Ruse
print('R usado = %.3f +- %.3f' % (Ruse['R'], Ruse['err']))

# ---------------- Method 1: QCD in the OS analysis region (events tree), yields and kappa shape
ss = data_minus_mc('ev', lambda t: t['isOS'] == 0)
qcd_n = Ruse['R'] * max(ss[0], 0.)
qcd_err = np.sqrt((Ruse['R'] ** 2) * ss[1] + (Ruse['err'] * max(ss[0], 0.)) ** 2)
osd = float(ak.sum(S['data']['ev']['isOS'] == 1))
res['metodo1_eventos'] = dict(SS_datos=ss[2], SS_mc=ss[3], QCD_OS=qcd_n, QCD_OS_err=qcd_err, OS_datos=osd,
                              fraccion_QCD_en_OS=qcd_n / osd if osd else float('nan'))
print('Método 1: QCD_OS = %.1f +- %.1f eventos  (datos OS = %d, SS datos = %d, SS MC = %.1f)' % (qcd_n, qcd_err, osd, ss[2], ss[3]))

def vertices(t, mask):
    """per event list of kappa of SVs with L_T > LT_CUT"""
    t = t[mask]
    sel = t['sv_LT'] > LT_CUT
    return t['sv_k'][sel]

def fneg_boot(kev, nboot=2000):
    """f(kappa<0) over vertices, error from bootstrapping events"""
    kev = [np.asarray(x) for x in ak.to_list(kev) if len(x)]
    if not kev: return float('nan'), float('nan'), 0, 0
    neg = np.array([np.sum(x < 0) for x in kev]); tot = np.array([len(x) for x in kev])
    f = neg.sum() / tot.sum()
    idx = rng.integers(0, len(kev), size=(nboot, len(kev)))
    fb = neg[idx].sum(1) / tot[idx].sum(1)
    return float(f), float(fb.std()), int(tot.sum()), len(kev)

dEV = S['data']['ev']
k_os = vertices(dEV, dEV['isOS'] == 1); k_ss = vertices(dEV, dEV['isOS'] == 0)
k_os_anti = vertices(dEV, (dEV['isOS'] == 1) & iso_reg(dEV, True))
k_os_iso = vertices(dEV, (dEV['isOS'] == 1) & iso_reg(dEV, False))
fn = {}
for name, kk in [('datos_OS', k_os), ('datos_SS (forma QCD)', k_ss), ('datos_OS_antiaislado', k_os_anti), ('datos_OS_aislado', k_os_iso)]:
    f, e, nv, ne = fneg_boot(kk)
    fn[name] = dict(f_kneg=f, err_eventos=e, vertices=nv, eventos=ne)
    print('f(k<0) %-22s = %.3f +- %.3f  (%d vértices en %d eventos)' % (name, f, e, nv, ne))
res['f_kneg'] = fn

# histograms: data OS vs QCD (SS x R) + MC (OS); MC only for completeness (1 file each)
def H(kev, w=1.):
    x = ak.to_numpy(ak.flatten(kev)) if len(kev) else np.array([])
    return np.histogram(np.clip(x, BINS[0] + 1e-6, BINS[-1] - 1e-6), BINS)[0] * w
h_os = H(k_os); h_qcd = H(k_ss, Ruse['R'])
h_mc = np.zeros(len(BINS) - 1)
for s in MC:
    t = S[s]['ev']; m = t['isOS'] == 1
    sel = t['sv_LT'][m] > LT_CUT
    k = ak.to_numpy(ak.flatten(t['sv_k'][m][sel])); w = ak.to_numpy(ak.flatten(ak.broadcast_arrays(t['genW'][m], t['sv_k'][m])[0][sel]))
    h_mc += np.histogram(np.clip(k, BINS[0] + 1e-6, BINS[-1] - 1e-6), BINS, weights=w * S[s]['w'])[0] if len(k) else 0
c = 0.5 * (BINS[1:] + BINS[:-1])
fig, ax = plt.subplots(figsize=(10, 6))
# Only QCD is shown (the user wants the QCD background only); MC enters only through the subtraction in
# the control regions. h_mc is still saved in the JSON for reference.
ax.bar(c, h_qcd, width=10, color='#bbbbbb', label='QCD desde datos: SS × R (R = %.2f)' % Ruse['R'])
ax.errorbar(c, h_os, yerr=np.sqrt(h_os), fmt='ko', ms=4, label='Datos OS')
ax.set_yscale('symlog', linthresh=1); ax.set_xlabel('κ∥ = L_T · P_T (mm·GeV)'); ax.set_ylabel('vértices / 10 mm·GeV')
ax.set_title('Vértices con L_T > 0.02 mm, %.0f pb⁻¹' % L); ax.legend(frameon=False); ax.grid(alpha=0.2)
fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'kappa_qcd.png'), dpi=140)
res['hist'] = dict(bins=BINS.tolist(), datos_OS=h_os.tolist(), QCD=h_qcd.tolist(), MC=h_mc.tolist())

# ---------------- m_ee at level A, four regions (sanity: Z peak in OS-iso, flat SS/anti)
dA = S['data']['A']
fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
mb = np.linspace(0, 300, 61)
for ax, anti in zip(axs, [False, True]):
    for os_flag, col in [(1, 'k'), (0, '#e41a1c')]:
        m = (dA['isOS'] == os_flag) & iso_reg(dA, anti)
        ax.hist(ak.to_numpy(dA['mee'][m]), mb, histtype='step', color=col, lw=1.6, label=('OS' if os_flag else 'SS'))
    ax.set_yscale('log'); ax.set_xlabel('m_ee (GeV)'); ax.set_title('Nivel A, ' + ('anti-aislados' if anti else 'aislados')); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'mee_regiones.png'), dpi=140)

# ---------------- Method 2: tight-to-loose fake factor (cross-check)
def eta_bin(eta): return (np.abs(eta) > 1.479).astype(int)   # 0 barrel, 1 endcap
def electrons(A, mask):
    t = A[mask]
    return (ak.to_numpy(ak.flatten(t['e_idBits'])), ak.to_numpy(ak.flatten(t['e_eta'])),
            ak.to_numpy(ak.flatten(ak.broadcast_arrays(t['genW'], t['e_eta'])[0])))
F = {}
mreg = lambda t: (t['isOS'] == 0) & ((t['mee'] < 70) | (t['mee'] > 110))
for b, nm in [(0, 'barril'), (1, 'endcap')]:
    num = den = vn = vd = 0.
    for s in ['data'] + MC:
        bits, eta, g = electrons(S[s]['A'], mreg(S[s]['A']))
        loose = (bits & 8) > 0; tight = (bits & 4) > 0; inb = eta_bin(eta) == b
        sgn = 1. if s == 'data' else -S[s]['w']
        wts = np.ones_like(eta) if s == 'data' else g
        num += sgn * wts[inb & tight].sum(); den += sgn * wts[inb & loose & ~tight].sum()
        vn += (wts[inb & tight] ** 2).sum() * sgn ** 2; vd += (wts[inb & loose & ~tight] ** 2).sum() * sgn ** 2
    f, e = ratio(num, vn, den, vd)
    F[nm] = dict(F=f, err=e, tight=num, loose_no_tight=den)
    print('F(%s) = %.3f +- %.3f   (tight %.0f, loose-no-tight %.0f)' % (nm, f, e, num, den))
res['metodo2_F'] = F
Fv = np.array([F['barril']['F'], F['endcap']['F']])
t = dEV[dEV['isOS'] == 1]
bits = np.asarray(ak.to_numpy(ak.fill_none(ak.pad_none(t["e_idBits"], 2, clip=True), 0)), dtype=int).reshape(-1, 2)
eta = np.asarray(ak.to_numpy(ak.fill_none(ak.pad_none(t["e_eta"], 2, clip=True), 0.)), dtype=float).reshape(-1, 2)
tight = (bits & 4) > 0; lnt = ((bits & 8) > 0) & ~tight
both_t = tight.all(1)
one_f = (tight[:, 0] & lnt[:, 1]) | (lnt[:, 0] & tight[:, 1])
two_f = lnt.all(1)
Fe = np.nan_to_num(Fv[eta_bin(eta)])
pred = (np.where(tight[:, 0] & lnt[:, 1], Fe[:, 1], 0) + np.where(lnt[:, 0] & tight[:, 1], Fe[:, 0], 0)).sum() - (Fe[:, 0] * Fe[:, 1])[two_f].sum()
res['metodo2_region_tight'] = dict(datos_OS_ambos_tight=int(both_t.sum()), eventos_1_falla=int(one_f.sum()),
                                   eventos_2_fallan=int(two_f.sum()), falsos_predichos=float(pred))
print('Método 2 (región con ambos electrones tight): datos OS = %d, falsos predichos = %.1f' % (both_t.sum(), pred))

json.dump(res, open(os.path.join(args.outdir, 'qcd_numeros.json'), 'w'), indent=1, default=float)
with open(os.path.join(args.outdir, 'qcd_resumen.md'), 'w') as f:
    f.write('# QCD desde datos (L = %.1f pb⁻¹, aislamiento < %.2f)\n\n' % (L, args.iso))
    f.write('| región para R | R = OS/SS (anti-aislado) | OS datos | SS datos |\n|---|---|---|---|\n')
    for k, v in R.items(): f.write('| %s | %.3f ± %.3f | %d | %d |\n' % (k, v['R'], v['err'], v['OS_datos'], v['SS_datos']))
    m = res['metodo1_eventos']
    f.write('\n**Método 1:** QCD_OS = R × (SS datos − SS MC) = %.1f ± %.1f eventos de %d OS (%.0f %%).\n\n' % (
        m['QCD_OS'], m['QCD_OS_err'], m['OS_datos'], 100 * m['fraccion_QCD_en_OS']))
    f.write('| muestra | f(κ∥<0) | vértices | eventos |\n|---|---|---|---|\n')
    for k, v in fn.items(): f.write('| %s | %.3f ± %.3f | %d | %d |\n' % (k, v['f_kneg'], v['err_eventos'], v['vertices'], v['eventos']))
    f.write('\n**Método 2 (tight-to-loose):** F barril = %.3f ± %.3f, F endcap = %.3f ± %.3f; región OS con ambos tight: datos %d, falsos predichos %.1f.\n' % (
        F['barril']['F'], F['barril']['err'], F['endcap']['F'], F['endcap']['err'], both_t.sum(), pred))
print('Guardado en', args.outdir)
