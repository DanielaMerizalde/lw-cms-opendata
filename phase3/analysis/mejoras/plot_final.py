#!/usr/bin/env python3
"""v3 final: Fig.-2-style kappa_par plots, numbers and cutflow on data + MC + signal.
Selection: v2 trigger+objects (TF/TO/HQ/JetS), OS (SS for QCD), chi2 mass assignment (disjoint jet pairs,
m_jj~m_Z, m_ejj~200), chi2<6 per electron, adaptive vertex fit of all e+jj tracks (no cleaning),
kappa = (PV->SV)_T . P_T(SV tracks) [mm GeV].   Usage: ../.venv/bin/python plot_final.py
"""
import glob, os, json
import numpy as np, uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out_data'); PL = os.path.join(HERE, 'plots_final'); os.makedirs(PL, exist_ok=True)
MZ, M, SJJ, SEJJ, CHI2MAX = 91.19, 200.0, 15.9, 16.9, 6.0
L_PROC = json.load(open(os.path.join(HERE, '..', 'lumi_processed.json')))['L_processed_pb']
L_FULL = 11467.0
XS = {'DY': 3503.7, 'TT': 225.2, 'W1': 6662.8, 'W2': 2159.2, 'W3': 640.4}
SIG_XS, BR2 = 5.97e-3, 0.4887
SYST = np.sqrt(sum(x ** 2 for x in [18, 3, 1, 3, 2, 3, 1])) / 100.

def load(s):
    dn = os.path.join(HERE, 'done_final', s + '.txt')
    done = set(l.strip() for l in open(dn)) if os.path.exists(dn) else set()
    fs = [f for f in sorted(glob.glob(os.path.join(OUT, s, '*.root'))) if os.path.basename(f)[:-5] in done]
    if not fs: return None
    cut = 0; cutw = 0; evs = []
    for f in fs:
        try:
            r = uproot.open(f)
            cut = cut + r['wdv3/cutflow'].values(); cutw = cutw + r['wdv3/cutflow_w'].values()
            evs += ak.to_list(r['wdv3/events'].arrays(filter_name=['isOS', 'genW', 'pvx', 'pvy', 'e_*', 'c_*', 'f_*']))
        except Exception as e:
            print('skip', f, e)
    return dict(cut=cut, cutw=cutw, ev=evs, nfiles=len(fs))

def chi(e, i): return ((e['c_mjj'][i] - MZ) / SJJ) ** 2 + ((e['c_mejj'][i] - M) / SEJJ) ** 2

def select(e):
    """returns list of SV dicts (one per electron at most) for this event"""
    c0 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 0]
    c1 = [i for i in range(len(e['c_ele'])) if e['c_ele'][i] == 1]
    best, bc = None, 1e99
    for i in c0:
        for j in c1:
            if {e['c_j1'][i], e['c_j2'][i]} & {e['c_j1'][j], e['c_j2'][j]}: continue
            c = chi(e, i) + chi(e, j)
            if c < bc: bc, best = c, (i, j)
    if best is None:
        cs = sorted(c0 + c1, key=lambda i: chi(e, i))
        best = tuple(cs[:1])
    out = []
    for ci in best:
        if chi(e, ci) >= CHI2MAX: continue
        js = [j for j in range(len(e['f_cand'])) if e['f_cand'][j] == ci and e['f_clean'][j] == 0 and e['f_fitter'][j] == 2]
        js = [j for j in js if e['f_hasEle'][j] == 1 and e['f_chi2'][j] < 5 and e['f_ntrk'][j] >= 3]
        if not js: continue
        j = js[0]
        dx, dy = e['f_x'][j] - e['pvx'], e['f_y'][j] - e['pvy']
        k = e['c_ele'][ci]
        out.append(dict(k=10 * (dx * e['f_ptx'][j] + dy * e['f_pty'][j]), LT=10 * np.hypot(dx, dy),
                        sig=(e['e_lw'][k] >= 0) if 'e_lw' in e else False, w=e['genW']))
    return out

S = {s: load(s) for s in ['data', 'DY', 'TT', 'W1', 'W2', 'W3', 'sig_causal', 'sig_acausal']}
avail = {s: (S[s]['nfiles'] if S[s] else 0) for s in S}
print('files:', avail)
SV, NEV = {}, {}
for s, d in S.items():
    if d is None: continue
    for ch in ['os', 'ss']:
        rows, nsel, nlt = [], 0, 0
        for e in d['ev']:
            if (e['isOS'] == 1) != (ch == 'os'): continue
            r = select(e)
            if r: nsel += 1
            if any(x['LT'] > 0.02 for x in r): nlt += 1
            rows += r
        SV[(s, ch)] = rows; NEV[(s, ch)] = (nsel, nlt)

def mcw(s, L):
    if s in XS: return XS[s] * L / S[s]['cutw'][0]
    return SIG_XS * BR2 * L / S[s]['cut'][0]

def arr(s, ch, LTcut, flip=False):
    rows = [r for r in SV.get((s, ch), []) if (not LTcut or r['LT'] > 0.02)]
    k = np.array([(-r['k'] if (flip and r['sig']) else r['k']) for r in rows]); w = np.array([r['w'] for r in rows], float)
    return k, w

def hists(bins, LTcut, L, sigscale=1000.):
    R = bins[-1]
    def H(k, w): return np.histogram(np.clip(k, bins[0] + 1e-6, R - 1e-6), bins, weights=w)[0] if len(k) else np.zeros(len(bins) - 1)
    out = {}
    kd, wd = arr('data', 'os', LTcut); out['data_raw'] = H(kd, wd)
    st2 = np.zeros(len(bins) - 1); mcss = np.zeros(len(bins) - 1)
    for g, mem in [('DY', ['DY']), ('W', ['W1', 'W2', 'W3']), ('TT', ['TT'])]:
        h = np.zeros(len(bins) - 1)
        for m in mem:
            if S[m] is None: continue
            k, w = arr(m, 'os', LTcut); sw = mcw(m, L); h += H(k, w * sw); st2 += H(k, (w * sw) ** 2)
            k, w = arr(m, 'ss', LTcut); mcss += H(k, w * sw)
        out[g] = h
    kss, wss = arr('data', 'ss', LTcut); hss = H(kss, wss) * (L / L_PROC)
    out['QCD'] = np.clip(hss - mcss, 0, None); st2 += hss * (L / L_PROC)
    out['stat2'] = st2
    for s, flip in [('sig_causal', True), ('sig_acausal', False)]:
        if S[s] is None: continue
        k, w = arr(s, 'os', LTcut, flip); out[s] = H(k, w * mcw(s, L) * sigscale)
    return out

def figure(bins, LTcut, L, fname, title_extra=''):
    h = hists(bins, LTcut, L)
    c = 0.5 * (bins[1:] + bins[:-1]); sc = L / L_PROC
    hd = h['data_raw'] * sc; ed = np.sqrt(h['data_raw']) * sc
    tot = h['DY'] + h['W'] + h['TT'] + h['QCD']
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7, 7.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1], hspace=0.05))
    bottom = np.zeros(len(c))
    for g, col, lab in [('QCD', '#dddddd', 'QCD multijet (SS data)'), ('TT', '#999999', r'$t\bar{t}$'),
                        ('W', '#444444', 'W+jets'), ('DY', '#e41a1c', r'$Z\to\ell\ell$')]:
        ax.bar(c, h[g], width=np.diff(bins), bottom=bottom, color=col, label=lab, linewidth=0); bottom = bottom + h[g]
    band = np.sqrt((tot * SYST) ** 2 + h['stat2'])
    ax.fill_between(bins, np.append(tot - band, (tot - band)[-1]), np.append(tot + band, (tot + band)[-1]), step='post',
                    facecolor='none', edgecolor='#666666', hatch='////', linewidth=0)
    if 'sig_causal' in h:
        ax.step(bins, np.append(h['sig_causal'], h['sig_causal'][-1]), where='post', color='#ff7f50', ls='-.', lw=1.8,
                label=r'lwe$\to$Ze causal, $\kappa\to-\kappa$ ($\times$1000)')
    if 'sig_acausal' in h:
        ax.step(bins, np.append(h['sig_acausal'], h['sig_acausal'][-1]), where='post', color='#1b9e77', ls=':', lw=2,
                label=r'lwe$\to$Ze acausal, reflejado ($\times$1000)')
    ax.errorbar(c, hd, yerr=ed, fmt='o', color='k', ms=4, label='Data' + (' (×%.0f)' % sc if sc > 1.01 else ''))
    ax.set_yscale('log'); ax.set_ylim(0.3 if sc < 2 else 3, max(10, hd.max(), tot.max()) * 20)
    ax.set_ylabel('Displaced vertices/bin'); ax.legend(fontsize=7.5, frameon=False, loc='upper right')
    ax.text(0.02, 1.01, 'CMS Open Data', transform=ax.transAxes, fontweight='bold')
    ax.text(1.0, 1.01, r'%s (2012, 8 TeV) — v3 final%s' % (('%.0f pb$^{-1}$' % L) if L < 1000 else ('%.2f fb$^{-1}$' % (L / 1000)), title_extra),
            transform=ax.transAxes, ha='right', fontsize=8)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(tot > 0, hd / tot, np.nan); re = np.where(tot > 0, ed / tot, np.nan); rb = np.where(tot > 0, band / tot, np.nan)
    rx.errorbar(c, r, yerr=re, fmt='o', color='k', ms=3)
    rx.fill_between(bins, np.append(1 - rb, (1 - rb)[-1]), np.append(1 + rb, (1 + rb)[-1]), step='post', facecolor='none', edgecolor='#666666', hatch='////', linewidth=0)
    rx.axhline(1, color='k', ls='--', lw=0.8); rx.set_yscale('log'); rx.set_ylim(0.1, 10)
    rx.set_ylabel('data/MC'); rx.set_xlabel(r'$\kappa_\parallel$ (mm$\cdot$GeV)'); rx.set_xlim(bins[0], bins[-1])
    fig.savefig(os.path.join(PL, fname + '.png'), dpi=150, bbox_inches='tight'); fig.savefig(os.path.join(PL, fname + '.pdf'), bbox_inches='tight')
    plt.close(fig)
    return h, tot, hd

B150 = np.linspace(-150, 150, 31); B30 = np.linspace(-30, 30, 31)
figure(B150, True, L_PROC, 'fig2_v3_LT002')
figure(B150, False, L_PROC, 'fig2_v3_noLT')
figure(B30, True, L_PROC, 'fig2_v3_LT002_zoom30')
h_full, tot_full, hd_full = figure(B150, True, L_FULL, 'fig2_v3_LT002_full', ' (escalado)')

# side by side with the paper's Fig. 2
pf = os.path.join(HERE, '..', '..', '..', 'docs', 'figuras_signo', 'paper_fig2.png')
if os.path.exists(pf):
    fig, axs = plt.subplots(1, 2, figsize=(14, 7.5))
    axs[0].imshow(plt.imread(pf)); axs[0].set_title('Sánchez 2023, Fig. 2 (11.5 fb$^{-1}$)', fontsize=10)
    axs[1].imshow(plt.imread(os.path.join(PL, 'fig2_v3_LT002_full.png'))); axs[1].set_title('Este trabajo, v3 final (113 pb$^{-1}$ escalado a 11.47 fb$^{-1}$)', fontsize=10)
    for a in axs: a.axis('off')
    fig.savefig(os.path.join(PL, 'fig2_paper_vs_v3.png'), dpi=130, bbox_inches='tight'); plt.close(fig)

# numbers
def fneg(s, ch='os', LTcut=True, flip=False, weighted=False):
    k, w = arr(s, ch, LTcut, flip)
    if len(k) == 0: return None
    if not weighted: n = len(k); f = (k < 0).mean(); return [float(f), float(np.sqrt(f * (1 - f) / n)), n]
    W = w.sum(); f = w[k < 0].sum() / W; neff = W ** 2 / (w ** 2).sum(); return [float(f), float(np.sqrt(max(f * (1 - f), 0) / neff)), len(k)]
res = dict(L_proc_pb=L_PROC, files=avail, chi2=dict(MZ=MZ, M=M, sjj=SJJ, sejj=SEJJ, chi2max=CHI2MAX))
for LTcut in [True, False]:
    tag = 'LT002' if LTcut else 'noLT'
    d = {}
    for s in ['data', 'DY', 'TT', 'W1', 'W2', 'W3', 'sig_acausal']:
        if S[s] is not None: d[s] = fneg(s, 'os', LTcut, weighted=(s == 'TT'))
    d['data_SS(QCD)'] = fneg('data', 'ss', LTcut)
    if S['sig_causal']: d['sig_causal'] = fneg('sig_causal', 'os', LTcut); d['sig_causal_flipped'] = fneg('sig_causal', 'os', LTcut, flip=True)
    # total MC (weighted)
    ks, ws = [], []
    for m in ['DY', 'TT', 'W1', 'W2', 'W3']:
        if S[m] is None: continue
        k, w = arr(m, 'os', LTcut); ks.append(k); ws.append(w * mcw(m, L_PROC))
    k, w = arr('data', 'ss', LTcut); ks.append(k); ws.append(w)   # QCD template (SS data) added with its yield
    K, W = np.concatenate(ks), np.concatenate(ws)
    if len(K):
        f = W[K < 0].sum() / W.sum(); neff = W.sum() ** 2 / (W ** 2).sum()
        d['MC_total(+QCD_SS)'] = [float(f), float(np.sqrt(f * (1 - f) / neff)), len(K)]
    h = hists(B150, LTcut, L_PROC)
    yields = {g: float(h[g].sum()) for g in ['DY', 'W', 'TT', 'QCD']}; yields['MC_total'] = sum(yields.values())
    yields['data'] = float(h['data_raw'].sum())
    yields['data/MC'] = yields['data'] / yields['MC_total'] if yields['MC_total'] > 0 else None
    for s in ['sig_causal', 'sig_acausal']:
        if s in h: yields[s + '_xBR2'] = float(h[s].sum() / 1000.)
    res[tag] = dict(fneg=d, yields_Lproc=yields, nevents_sel={'%s_%s' % k: v for k, v in NEV.items()})
# peak bins scaled to full lumi
c = 0.5 * (B150[1:] + B150[:-1])
res['full_lumi_LT002'] = dict(data_bins_m10_0_and_0_10=[float(hd_full[14]), float(hd_full[15])],
                              MC_bins_m10_0_and_0_10=[float(tot_full[14]), float(tot_full[15])],
                              sig_acausal_x1000_peak=float(h_full.get('sig_acausal', np.zeros(30)).max()),
                              sig_causal_flip_x1000_peak=float(h_full.get('sig_causal', np.zeros(30)).max()))
# cutflow
names = ['NF', 'TF', 'TO', 'HQ', 'JetS', 'OS']
lines = ['| muestra | ' + ' | '.join(names) + ' | SV v3 (OS) | SV v3 + L_T>0.02 (OS) | SV v3 (SS) |', '|' + '---|' * 10]
for s in S:
    if S[s] is None: continue
    cu = S[s]['cut']
    lines.append('| %s (crudo) | ' % s + ' | '.join('%d' % x for x in cu) + ' | %d | %d | %d |' % (NEV[(s, 'os')][0], NEV[(s, 'os')][1], NEV[(s, 'ss')][0]))
    if s != 'data':
        sw = mcw(s, L_FULL) if s in XS else SIG_XS * BR2 * L_FULL / S[s]['cut'][0]
        cw = S[s]['cutw'] * sw
        lines.append('| %s (×σL, 11.47 fb⁻¹) | ' % s + ' | '.join('%.4g' % x for x in cw) + ' | %.4g | %.4g | %.4g |' % (NEV[(s, 'os')][0] * sw, NEV[(s, 'os')][1] * sw, NEV[(s, 'ss')][0] * sw))
    else:
        f = L_FULL / L_PROC
        lines.append('| data (×%.1f) | ' % f + ' | '.join('%.4g' % (x * f) for x in cu) + ' | %.4g | %.4g | %.4g |' % (NEV[(s, 'os')][0] * f, NEV[(s, 'os')][1] * f, NEV[(s, 'ss')][0] * f))
open(os.path.join(PL, 'cutflow_v3final.md'), 'w').write('# Cutflow v3 final\n\nMC sin pesos de PU; TT con signos de pesos. Señal ×BR(Z→had)²; sin BR (convención tesis) = ×2.046.\n\n' + '\n'.join(lines) + '\n')
json.dump(res, open(os.path.join(PL, 'numbers_v3final.json'), 'w'), indent=1)
print('\n'.join(lines)); print(json.dumps(res, indent=1))
