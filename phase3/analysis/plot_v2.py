#!/usr/bin/env python3
"""v2 (thesis convention) plots and tables:
  - cutflow side by side with thesis Table 2.2 (scaled to the full 11.467 fb^-1 and as efficiencies
    relative to the previous cut);
  - Fig. 2.5-style kappa_par histogram (SG stage, SV with L_T > 0.02 mm, kappa transverse with P_T of SV tracks);
  - signal-only plot: causal (as reco), causal flipped for truth-matched signal electrons, acausal reflected.
Signal ntuples are optional.  Usage: .venv/bin/python plot_v2.py [--kappa k|kobjT|k3trk|k3obj]
"""
import argparse, glob, json, os, sys
import numpy as np
import uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out'); PLOTS = os.path.join(HERE, 'plots'); os.makedirs(PLOTS, exist_ok=True)
L_FULL = 11467.0                       # pb^-1
N_DATA_FULL = 66235981                 # events in DoublePhoton B + C AOD (= thesis NF)
XS = {'DY': 3503.7, 'TT': 225.2, 'W1': 6662.8, 'W2': 2159.2, 'W3': 640.4}   # pb
SIG_XS = 5.97e-3                       # pb, paper/thesis Z-only M=200
BR2 = 0.4887                           # BR(Z->had)^2 (our convention); thesis: Z forced to quarks
SYST = np.sqrt(sum(x ** 2 for x in [18, 3, 1, 3, 2, 3, 1])) / 100.
CUTS = ['NF', 'TF', 'TO', 'HQ', 'JetS', 'DRC', 'SG', 'IPP']
THESIS = {
    'Data': [66235981, 5816590, 2318120, 2251784, 69803, 68795, 48857, 144],
    'DY': [40176928, 3953503.5, 2005875, 1971623, 38282, 37547, 31849, 10.6],
    'TTbar': [2582368, 28237.1, 14889, 14653, 3965, 3696, 2740, 22.5],
    'WJets': [96706945, 46511.5, 15608, 15297, 595, 590, 330, 2.5],
    'QCD': [None, 224649, 12140, 9755, 4721, 4768, 1665, 55.1],
    'LW200': [67.7, 51.2, 28.8, 28.4, 11.4, 10.7, 10.4, 0.02436],
}

def load(sample):
    files = [f for f in sorted(glob.glob(os.path.join(OUT, sample, '*.root'))) if os.path.getsize(f) > 0]
    if not files: return None
    d = dict(cos=0, css=0, cosw=0, cssw=0, ev=[], n=0)
    for f in files:
        try:
            with uproot.open(f) as r:
                d['cos'] = d['cos'] + r['wdv/cutflow_os'].values(); d['css'] = d['css'] + r['wdv/cutflow_ss'].values()
                d['cosw'] = d['cosw'] + r['wdv/cutflow_os_w'].values(); d['cssw'] = d['cssw'] + r['wdv/cutflow_ss_w'].values()
                d['ev'].append(r['wdv/events'].arrays()); d['n'] += 1
        except Exception as e:
            print('skip', f, e, file=sys.stderr)
    if not d['n']: return None
    d['ev'] = ak.concatenate(d['ev'])
    return d

def sv_values(d, charge, kvar, flip=False, stage='SG'):
    """kappa of SVs at SG (or IPP) stage with L_T > 0.02 mm; flip sign for truth-matched signal electrons."""
    ev = d['ev']
    sel = (ev['isOS'] == 1) if charge == 'os' else (ev['isSS'] == 1)
    if stage == 'IPP':
        sel = sel & (ev['passIPPflip' if flip else 'passIPP'] == 1)
    e = ev[sel]
    k = e['sv_' + kvar]
    good = e['sv_LT'] > 0.02
    if flip:
        k = ak.where(e['sv_sig'] == 1, -k, k)
    k = k[good]
    w = ak.broadcast_arrays(e['genW'], k)[0]
    return ak.to_numpy(ak.flatten(k)).astype(float), ak.to_numpy(ak.flatten(w)).astype(float)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kappa', default='k')
    ap.add_argument('--range', type=float, default=150.)
    ap.add_argument('--nbins', type=int, default=30)
    ap.add_argument('--sigscale', type=float, default=1000.)
    a = ap.parse_args()
    S = {s: load(s) for s in ['data', 'DY', 'TT', 'W1', 'W2', 'W3', 'sig_causal', 'sig_acausal']}
    if S['data'] is None: sys.exit('no data ntuples')
    nNF = S['data']['cos'][0]
    lumi = json.load(open(os.path.join(HERE, 'lumi_processed.json'))) if os.path.exists(os.path.join(HERE, 'lumi_processed.json')) else {}
    # processed fraction: byte fraction of the fully processed files (lumi_calc.py); fallback: events read / full dataset
    fdata = lumi['L_processed_pb'] / L_FULL if lumi.get('L_processed_pb') else nNF / N_DATA_FULL
    L_proc = L_FULL * fdata
    print('data events read %d -> fraction %.4f -> L_proc ~ %.1f pb^-1 (byte-fraction estimate: %s)' % (nNF, fdata, L_proc, lumi.get('L_processed_pb')))

    def mcscale(s, L):  # weight per unit raw (signed) event
        return XS[s] * L / S[s]['cosw'][0]
    def sigscale(s, L, br=True):
        return SIG_XS * (BR2 if br else 1.) * L / S[s]['cosw'][0]

    # ---------------- cutflow tables
    rows = {}
    rows['Data'] = S['data']['cos'] / fdata
    mcs = {'DY': ['DY'], 'TTbar': ['TT'], 'WJets': ['W1', 'W2', 'W3']}
    for g, mem in mcs.items():
        r = np.zeros(8); ss = np.zeros(8)
        for m in mem:
            if S[m] is None: continue
            r += S[m]['cosw'] * mcscale(m, L_FULL); ss += S[m]['cssw'] * mcscale(m, L_FULL)
        rows[g] = r; rows[g + '_SS'] = ss
    # QCD: SS data minus SS MC (fitted in the SS region), extrapolated to OS with R=1; defined at SG and IPP
    q = np.full(8, np.nan)
    dss = S['data']['css'] / fdata
    mcss = rows['DY_SS'] + rows['TTbar_SS'] + rows['WJets_SS']
    for i in [6, 7]:
        q[i] = max(dss[i] - mcss[i], 0.)
    rows['QCD'] = q
    raw = {'Data': S['data']['cos'], 'DY': S['DY']['cos'] if S['DY'] else None, 'TTbar': S['TT']['cos'] if S['TT'] else None,
           'WJets': sum(S[m]['cos'] for m in ['W1', 'W2', 'W3'] if S[m]), 'QCD(SS data)': S['data']['css']}
    for s in ['sig_causal', 'sig_acausal']:
        if S[s] is None: continue
        c = S[s]['cosw'].copy()
        if True:   # IPP with the thesis flip for the causal sample, no flip for the acausal one
            ev = S[s]['ev']
            c[7] = ak.sum((ev['isOS'] == 1) & (ev['passIPPflip' if s == 'sig_causal' else 'passIPP'] == 1))
        rows[s + ' (x BR^2)'] = c * sigscale(s, L_FULL, True)
        rows[s + ' (thesis, no BR)'] = c * sigscale(s, L_FULL, False)
        raw[s] = c
    def eff(v):
        out = [None]
        for i in range(1, 8):
            out.append(v[i] / v[i - 1] if (v[i - 1] and v[i - 1] > 0 and v[i] == v[i] and v[i - 1] == v[i - 1]) else None)
        return out
    def fmt(x, p='%.4g'):
        return '-' if x is None or (isinstance(x, float) and np.isnan(x)) else p % x
    lines = ['# Cutflow v2 vs tesis (Tabla 2.2), escalado a L = 11.467 fb^-1', '',
             'Datos procesados: %d eventos (NF) = fracción %.4f del dataset completo -> L_proc ≈ %.1f pb^-1. '
             'MC: 1 archivo online por muestra. Señal: σ = 5.97 fb (× BR(Z→had)² = 0.4887 en nuestra convención). '
             'IPP de la señal causal con el flip de la tesis (κ→−κ para SV del electrón de señal).' % (nNF, fdata, L_proc), '',
             '## Conteos escalados a L completa (nuestro / tesis)', '',
             '| corte | ' + ' | '.join('%s nuestro | %s tesis' % (k, k) for k in ['Data', 'DY', 'TTbar', 'WJets', 'QCD']) + ' | LW200 nuestro (×BR²) | LW200 nuestro (sin BR, tesis) | LW200 tesis |',
             '|' + '---|' * 14]
    sc = 'sig_causal'
    for i, c in enumerate(CUTS):
        cells = []
        for k in ['Data', 'DY', 'TTbar', 'WJets', 'QCD']:
            cells += [fmt(rows[k][i]), fmt(THESIS[k][i])]
        s1 = rows.get(sc + ' (x BR^2)'); s2 = rows.get(sc + ' (thesis, no BR)')
        cells += [fmt(s1[i] if s1 is not None else None), fmt(s2[i] if s2 is not None else None), fmt(THESIS['LW200'][i])]
        lines.append('| %s | ' % c + ' | '.join(cells) + ' |')
    lines += ['', '## Eficiencias relativas al corte anterior (nuestro / tesis)', '',
              '| corte | ' + ' | '.join('%s nuestro | %s tesis' % (k, k) for k in ['Data', 'DY', 'TTbar', 'WJets', 'LW200']) + ' | LW200 acausal nuestro |',
              '|' + '---|' * 12]
    E = {k: eff(rows[k]) for k in ['Data', 'DY', 'TTbar', 'WJets']}
    E['LW200'] = eff(rows[sc + ' (x BR^2)']) if sc + ' (x BR^2)' in rows else [None] * 8
    Ea = eff(rows['sig_acausal (x BR^2)']) if 'sig_acausal (x BR^2)' in rows else [None] * 8
    T = {k: eff([x if x is not None else np.nan for x in THESIS[k if k != 'LW200' else 'LW200']]) for k in ['Data', 'DY', 'TTbar', 'WJets', 'LW200']}
    for i, c in enumerate(CUTS):
        if i == 0: continue
        cells = []
        for k in ['Data', 'DY', 'TTbar', 'WJets', 'LW200']:
            cells += [fmt(E[k][i], '%.3f'), fmt(T[k][i], '%.3f')]
        cells.append(fmt(Ea[i], '%.3f'))
        lines.append('| %s | ' % c + ' | '.join(cells) + ' |')
    lines += ['', '## Conteos crudos (sin escalar; OS; MC = suma de signos de pesos para TT en filas escaladas)', '',
              '| muestra | ' + ' | '.join(CUTS) + ' |', '|' + '---|' * 9]
    for k, v in raw.items():
        if v is None: continue
        lines.append('| %s | ' % k + ' | '.join('%d' % x for x in v) + ' |')
    lines.append('| data SS chain | ' + ' | '.join('%d' % x for x in S['data']['css']) + ' |')
    open(os.path.join(PLOTS, 'cutflow_v2.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

    # ---------------- Fig 2.5-style kappa plot (SG stage, L_T > 0.02 mm), scaled to L_proc
    R = a.range
    bins = np.linspace(-R, R, a.nbins + 1); c = 0.5 * (bins[1:] + bins[:-1])
    def H(k, w):
        return np.histogram(np.clip(k, -R + 1e-6, R - 1e-6), bins, weights=w)[0]
    kd, wd = sv_values(S['data'], 'os', a.kappa); hd = H(kd, wd)
    mc, mcss_h, stat2 = {}, np.zeros(len(c)), np.zeros(len(c))
    for g, mem in mcs.items():
        h = np.zeros(len(c))
        for m in mem:
            if S[m] is None: continue
            k, w = sv_values(S[m], 'os', a.kappa); sw = mcscale(m, L_proc)
            h += H(k, w * sw); stat2 += H(k, (w * sw) ** 2)
            k, w = sv_values(S[m], 'ss', a.kappa); mcss_h += H(k, w * sw)
        mc[g] = h
    kss, wss = sv_values(S['data'], 'ss', a.kappa); hss = H(kss, wss)
    mc['QCD'] = np.clip(hss - mcss_h, 0, None); stat2 += hss
    tot = sum(mc.values())
    sig = {}
    for s, flip in [('sig_causal', True), ('sig_acausal', False)]:
        if S[s] is None: continue
        k, w = sv_values(S[s], 'os', a.kappa, flip=flip)
        sig[s] = H(k, w * sigscale(s, L_proc, True) * a.sigscale)
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7, 7.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1], hspace=0.05))
    bottom = np.zeros(len(c))
    for g, col, lab in [('QCD', '#dddddd', 'QCD multijet (SS data)'), ('TTbar', '#999999', r'$t\bar{t}$'),
                        ('WJets', '#444444', 'W+jets'), ('DY', '#e41a1c', r'$Z/\gamma^*\to\ell\ell$ (DY)')]:
        ax.bar(c, mc[g], width=np.diff(bins), bottom=bottom, color=col, label=lab, linewidth=0)
        bottom = bottom + mc[g]
    band = np.sqrt((tot * SYST) ** 2 + stat2)
    ax.fill_between(bins, np.append(tot - band, (tot - band)[-1]), np.append(tot + band, (tot + band)[-1]), step='post',
                    facecolor='none', edgecolor='#666666', hatch='////', linewidth=0, label='stat. ⊕ syst.')
    if 'sig_causal' in sig:
        ax.step(bins, np.append(sig['sig_causal'], sig['sig_causal'][-1]), where='post', color='#1b9e77', ls=':', lw=2,
                label=r'LW $M=200$, causal, $\kappa\to-\kappa$ ($\times%g$)' % a.sigscale)
    if 'sig_acausal' in sig:
        ax.step(bins, np.append(sig['sig_acausal'], sig['sig_acausal'][-1]), where='post', color='#7570b3', ls='--', lw=1.6,
                label=r'LW $M=200$, acausal reflected ($\times%g$)' % a.sigscale)
    ax.errorbar(c, hd, yerr=np.sqrt(hd), fmt='o', color='k', ms=4, label='Data')
    ax.set_yscale('log'); ax.set_ylim(0.1, max(10, hd.max(), tot.max()) * 30)
    ax.set_ylabel('Displaced vertices / %.0f mm·GeV' % (bins[1] - bins[0]))
    ax.legend(fontsize=7.5, frameon=False, loc='upper right')
    ax.text(0.02, 1.01, 'CMS Open Data', transform=ax.transAxes, fontweight='bold')
    ax.text(1.0, 1.01, r'%.3g pb$^{-1}$ (2012, 8 TeV)' % L_proc, transform=ax.transAxes, ha='right')
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(tot > 0, hd / tot, np.nan); re = np.where(tot > 0, np.sqrt(hd) / tot, np.nan); rb = np.where(tot > 0, band / tot, np.nan)
    rx.errorbar(c, r, yerr=re, fmt='o', color='k', ms=3)
    rx.fill_between(bins, np.append(1 - rb, (1 - rb)[-1]), np.append(1 + rb, (1 + rb)[-1]), step='post', facecolor='none',
                    edgecolor='#666666', hatch='////', linewidth=0)
    rx.axhline(1, color='k', lw=0.8, ls='--'); rx.set_ylim(0, 3)
    rx.set_ylabel('data/MC'); rx.set_xlabel(r'$\kappa_\parallel=\overrightarrow{PV\,SV}_T\cdot\vec P_T$ (mm$\cdot$GeV)')
    rx.set_xlim(-R, R)
    tag = '%s_r%g' % (a.kappa, R)
    fig.savefig(os.path.join(PLOTS, 'kappa_fig2p5_%s.png' % tag), dpi=150, bbox_inches='tight')
    fig.savefig(os.path.join(PLOTS, 'kappa_fig2p5_%s.pdf' % tag), bbox_inches='tight')
    plt.close(fig)

    def negfrac(k, w=None):
        n = len(k)
        if n == 0: return (None, None, 0)
        f = float((k < 0).sum()) / n
        return (f, float(np.sqrt(f * (1 - f) / n)), n)
    res = dict(kappa=a.kappa, L_proc_pb=L_proc, data_vertices=float(hd.sum()), data_vertices_unclipped=int(len(kd)),
               mc={g: float(v.sum()) for g, v in mc.items()}, mc_total=float(tot.sum()),
               data_over_bkg=float(hd.sum() / tot.sum()) if tot.sum() > 0 else None,
               negfrac_data=negfrac(kd), negfrac_data_SS=negfrac(kss))
    for s in sig: res['signal_' + s + '_xBR2_at_Lproc'] = float(sig[s].sum() / a.sigscale)

    # ---------------- signal-only plot
    if S['sig_causal'] is not None or S['sig_acausal'] is not None:
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        sb = np.linspace(-R, R, 31)
        for s, flip, col, ls, lab in [('sig_causal', False, '#999999', '-', 'causal (as reconstructed)'),
                                      ('sig_causal', True, '#1b9e77', ':', r'causal, $\kappa\to-\kappa$ for signal-e SVs (thesis)'),
                                      ('sig_acausal', False, '#7570b3', '--', 'acausal, reflected SV (true WDV)')]:
            if S[s] is None: continue
            k, w = sv_values(S[s], 'os', a.kappa, flip=flip)
            nf = negfrac(k)
            h = np.histogram(np.clip(k, -R + 1e-6, R - 1e-6), sb)[0]
            ax.step(sb, np.append(h, h[-1]), where='post', color=col, ls=ls, lw=1.8,
                    label='%s: N=%d, f(κ<0)=%.2f±%.2f' % (lab, nf[2], nf[0] or 0, nf[1] or 0))
            res['signal_negfrac %s' % lab] = nf
            # only SV of the truth-matched signal electron
            ev = S[s]['ev']; e = ev[ev['isOS'] == 1]
            kk = e['sv_' + a.kappa][(e['sv_LT'] > 0.02) & (e['sv_sig'] == 1)]
            kk = ak.to_numpy(ak.flatten(kk)).astype(float)
            if flip: kk = -kk
            res['signal_negfrac_sigEleOnly %s' % lab] = negfrac(kk)
        ax.set_xlabel(r'$\kappa_\parallel$ (mm$\cdot$GeV)'); ax.set_ylabel('SVs / bin (SG stage, $L_T>0.02$ mm)')
        ax.set_title(r'LW $M=200$ GeV, sólo-Z: flip vs reflexión', fontsize=9)
        ax.legend(fontsize=7.5, frameon=False); ax.set_xlim(-R, R)
        fig.savefig(os.path.join(PLOTS, 'signal_flip_vs_reflect_%s.png' % tag), dpi=150, bbox_inches='tight')
        fig.savefig(os.path.join(PLOTS, 'signal_flip_vs_reflect_%s.pdf' % tag), bbox_inches='tight')
        plt.close(fig)
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(PLOTS, 'kappa_fig2p5_%s.json' % tag), 'w'), indent=1)

if __name__ == '__main__':
    main()
