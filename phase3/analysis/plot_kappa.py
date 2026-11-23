#!/usr/bin/env python3
"""Fig. 2 reproduction (Sanchez 2023, ACI 15(1) 2780): stacked kappa_par histogram,
cutflow tables.  Reads ntuples produced by WDVAnalyzer (out/<sample>/*.root).

Usage: .venv/bin/python plot_kappa.py [--stage wdvc|sv] [--kappa obj|trk]
"""
import argparse, glob, json, os, sys
import numpy as np
import uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('WDV_OUT', os.path.join(HERE, 'out'))
PLOTS = os.environ.get('WDV_PLOTS', os.path.join(HERE, 'plots')); os.makedirs(PLOTS, exist_ok=True)

# luminosity bookkeeping written by lumi_calc.py
LUMI = json.load(open(os.environ.get('WDV_LUMI', os.path.join(HERE, 'lumi_processed.json'))))
L_PROC = LUMI['L_processed_pb']      # pb^-1
L_FULL = 11467.0                     # pb^-1 (4.412 + 7.055 fb^-1)

XS = {  # pb ; see README for sources
    'DY':  3503.7,
    'TT':  225.2,
    'W1':  6662.8,
    'W2':  2159.2,
    'W3':  640.4,
}
SIG_XS_PB = 5.97e-3 * 0.4887   # paper's Z-only sigma(M=200) x BR(Z->had)^2
SYST = np.sqrt(sum(x**2 for x in [18, 3, 1, 3, 2, 3, 1])) / 100.

def load(sample):
    files = sorted(glob.glob(os.path.join(OUT, sample, '*.root')))
    files = [f for f in files if os.path.getsize(f) > 0]
    if not files:
        return None
    arrs, cos, css, cosw, cssw = [], 0, 0, 0, 0
    good = []
    for f in files:
        try:
            with uproot.open(f) as r:
                cos = cos + r['wdv/cutflow_os'].values(); css = css + r['wdv/cutflow_ss'].values()
                cosw = cosw + r['wdv/cutflow_os_w'].values(); cssw = cssw + r['wdv/cutflow_ss_w'].values()
                arrs.append(r['wdv/events'].arrays())
                good.append(f)
        except Exception as e:
            print('skip', f, e, file=sys.stderr)
    if not good:
        return None
    return dict(ev=ak.concatenate(arrs), cos=cos, css=css, cosw=cosw, cssw=cssw, nfiles=len(good))

def vertices(d, charge, stage, kvar, sigflip=False):
    """per-vertex kappa values and per-vertex event weights (gen sign)"""
    ev = d['ev']
    sel = (ev['isOS'] == 1) if charge == 'os' else (ev['isSS'] == 1)
    sel = sel & (ev['passSG'] == 1)
    if stage == 'wdvc':
        sel = sel & (ev['passWDVC'] == 1)
    else:
        sel = sel & (ev['passSV'] == 1)
    e = ev[sel]
    good = (e['sv_flags'] & 64) > 0
    if stage == 'wdvc':
        wd = e['e_wdvc']
        # vertex belongs to an electron that passes WDVC
        good = good & (wd[e['sv_ele']] == 1)
    k = e['sv_k' + kvar][good]
    w = ak.broadcast_arrays(e['genW'], k)[0]
    k = ak.to_numpy(ak.flatten(k)); w = ak.to_numpy(ak.flatten(w))
    if sigflip:
        k = -k
    return k, w

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='wdvc', choices=['wdvc', 'sv'])
    ap.add_argument('--kappa', default='obj', choices=['obj', 'trk'])
    ap.add_argument('--sigscale', type=float, default=1000.)
    ap.add_argument('--lumi', default='proc', choices=['proc', 'full'])
    a = ap.parse_args()
    L = L_PROC if a.lumi == 'proc' else L_FULL
    bins = np.linspace(-150, 150, 31)
    S = {s: load(s) for s in ['data', 'DY', 'TT', 'W1', 'W2', 'W3', 'sig_causal', 'sig_acausal']}

    def mcw(s):
        d = S[s]; ngen = d['cosw'][0]
        return XS[s] * L / ngen

    def hist(s, charge, flip=False, scale=1.):
        k, w = vertices(S[s], charge, a.stage, a.kappa, flip)
        h, _ = np.histogram(np.clip(k, bins[0] + 1e-6, bins[-1] - 1e-6), bins, weights=w * scale)
        h2, _ = np.histogram(np.clip(k, bins[0] + 1e-6, bins[-1] - 1e-6), bins, weights=(w * scale) ** 2)
        return h, h2

    # data, scaled to lumi L if needed (data always is L_PROC)
    dscale = L / L_PROC
    hdata, _ = hist('data', 'os', scale=1.)
    mc = {}
    for grp, members in [('Z', ['DY']), ('W', ['W1', 'W2', 'W3']), ('tt', ['TT'])]:
        h = np.zeros(len(bins) - 1); h2 = np.zeros(len(bins) - 1)
        for m in members:
            if S[m] is None: continue
            x, x2 = hist(m, 'os', scale=mcw(m)); h += x; h2 += x2
        mc[grp] = (h, h2)
    # QCD from SS: data_SS - MC_SS, extrapolated with R_OS/SS = 1
    hss_raw, _ = hist('data', 'ss')
    hss = hss_raw * dscale
    mcss = np.zeros(len(bins) - 1)
    for m in ['DY', 'W1', 'W2', 'W3', 'TT']:
        if S[m] is None: continue
        mcss += hist(m, 'ss', scale=mcw(m))[0]
    hqcd = np.clip(hss - mcss, 0, None)
    mc['QCD'] = (hqcd, hss_raw * dscale**2)

    hd = hdata * dscale
    tot = sum(mc[g][0] for g in mc)
    totstat2 = sum(mc[g][1] for g in mc)

    # signal
    sig = {}
    for s, flip in [('sig_causal', True), ('sig_acausal', False)]:
        if S[s] is None: continue
        ngen = S[s]['cosw'][0]
        sig[s] = hist(s, 'os', flip=flip, scale=SIG_XS_PB * L / ngen * a.sigscale)[0]

    # ---- plot
    c = 0.5 * (bins[1:] + bins[:-1])
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7, 7.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1], hspace=0.05))
    order = [('QCD', '#dddddd', 'QCD multijet (SS data)'), ('tt', '#999999', r'$t\bar{t}$'),
             ('W', '#444444', 'W+jets'), ('Z', '#e41a1c', r'$Z\to\ell\ell$')]
    bottom = np.zeros_like(c)
    for g, col, lab in order:
        ax.bar(c, mc[g][0], width=np.diff(bins), bottom=bottom, color=col, label=lab, align='center', linewidth=0)
        bottom = bottom + mc[g][0]
    band = np.sqrt((tot * SYST) ** 2 + totstat2)
    ax.fill_between(bins, np.append(tot - band, (tot - band)[-1]), np.append(tot + band, (tot + band)[-1]),
                    step='post', facecolor='none', edgecolor='#777777', hatch='////', linewidth=0, label='stat. + syst.')
    if 'sig_causal' in sig:
        ax.step(bins, np.append(sig['sig_causal'], sig['sig_causal'][-1]), where='post', color='#ff7f50', ls='--', lw=1.8,
                label=r'$\tilde\ell\to Ze$ causal, $\kappa\to-\kappa$ ($\times%g$)' % a.sigscale)
    if 'sig_acausal' in sig:
        ax.step(bins, np.append(sig['sig_acausal'], sig['sig_acausal'][-1]), where='post', color='#1b9e77', ls=':', lw=1.8,
                label=r'$\tilde\ell\to Ze$ acausal (reflected SV) ($\times%g$)' % a.sigscale)
    ax.errorbar(c, hd, yerr=np.sqrt(hdata) * dscale, fmt='o', color='k', ms=4, label='Data' + ('' if a.lumi == 'proc' else ' (scaled)'))
    ax.set_yscale('log'); ax.set_ylim(0.3 * dscale * 0.1 + 0.03, max(1, (tot.max() if tot.max() > 0 else 1), hd.max()) * 30)
    ax.set_ylabel('Displaced vertices / bin')
    ax.legend(fontsize=8, frameon=False, ncol=1, loc='upper right')
    ax.text(0.02, 1.01, 'CMS Open Data', transform=ax.transAxes, fontweight='bold')
    ax.text(1.0, 1.01, r'%.3g fb$^{-1}$ (2012, 8 TeV)' % (L / 1000.), transform=ax.transAxes, ha='right')
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(tot > 0, hd / tot, np.nan)
        re = np.where(tot > 0, np.sqrt(hdata) * dscale / tot, np.nan)
        rb = np.where(tot > 0, band / tot, np.nan)
    rx.errorbar(c, r, yerr=re, fmt='o', color='k', ms=3)
    rx.fill_between(bins, np.append(1 - rb, (1 - rb)[-1]), np.append(1 + rb, (1 + rb)[-1]), step='post',
                    facecolor='none', edgecolor='#777777', hatch='////', linewidth=0)
    rx.axhline(1, color='k', lw=0.8, ls='--')
    rx.set_yscale('log'); rx.set_ylim(0.1, 10)
    rx.set_ylabel('data/MC'); rx.set_xlabel(r'$\kappa_\parallel$ (mm$\cdot$GeV)')
    rx.set_xlim(-150, 150)
    tag = '%s_%s_%s' % (a.stage, a.kappa, a.lumi)
    fig.savefig(os.path.join(PLOTS, 'kappa_fig2_%s.png' % tag), dpi=150, bbox_inches='tight')
    fig.savefig(os.path.join(PLOTS, 'kappa_fig2_%s.pdf' % tag), bbox_inches='tight')

    # ---- numbers
    res = dict(stage=a.stage, kappa=a.kappa, L_pb=L, data=float(hd.sum()),
               mc={g: float(mc[g][0].sum()) for g in mc}, mc_total=float(tot.sum()))
    def asym(h):
        n = h[c < 0].sum(); p = h[c > 0].sum()
        return float((p - n) / (p + n)) if (p + n) > 0 else float('nan')
    res['A_data'] = asym(hd); res['A_mc'] = asym(tot)
    for s in sig:
        res['sig_' + s] = float(sig[s].sum() / a.sigscale); res['A_' + s] = asym(sig[s])
    with np.errstate(divide='ignore', invalid='ignore'):
        res['data_over_mc'] = float(hd.sum() / tot.sum()) if tot.sum() > 0 else None
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(PLOTS, 'kappa_fig2_%s.json' % tag), 'w'), indent=1)

    # ---- cutflow table (raw events and weighted to L)
    names = ['All', 'TF', 'OS', 'SG', 'SV', 'WDVC']
    lines = ['| sample | chain | ' + ' | '.join(names) + ' |', '|' + '---|' * (len(names) + 2)]
    for s in S:
        if S[s] is None: continue
        for ch in ['os', 'ss']:
            raw = S[s]['c' + ch]
            lines.append('| %s | %s raw | ' % (s, ch.upper()) + ' | '.join('%d' % x for x in raw) + ' |')
            if s in XS:
                w = S[s]['c' + ch + 'w'] * XS[s] * L / S[s]['cosw'][0]
                lines.append('| %s | %s w(L) | ' % (s, ch.upper()) + ' | '.join('%.4g' % x for x in w) + ' |')
            elif s.startswith('sig'):
                w = S[s]['c' + ch + 'w'] * SIG_XS_PB * L / S[s]['cosw'][0]
                lines.append('| %s | %s w(L) | ' % (s, ch.upper()) + ' | '.join('%.4g' % x for x in w) + ' |')
    open(os.path.join(PLOTS, 'cutflow_%s.md' % a.lumi), 'w').write(
        '# Cutflow (L = %.1f pb^-1)\n\n' % L + '\n'.join(lines) + '\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
