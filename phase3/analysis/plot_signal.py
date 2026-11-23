#!/usr/bin/env python3
"""Signal kappa_par: causal sample with sign flipped (paper's method) vs acausal reflected sample
(true WDV geometry).  Also the unflipped causal distribution, cutflows and asymmetries."""
import os, sys, json, glob
import numpy as np
import uproot, awkward as ak
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_kappa import load, vertices, PLOTS

bins = np.linspace(-150, 150, 31)
c = 0.5 * (bins[1:] + bins[:-1])
S = {s: load(s) for s in ['sig_causal', 'sig_acausal']}
if not all(S.values()):
    print('signal ntuples missing', {k: v is not None for k, v in S.items()}); sys.exit(1)
res = {}
for stage in ['sv', 'wdvc']:
    for kv in ['obj', 'trk']:
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        out = {}
        for s, flip, col, ls, lab in [('sig_causal', False, '#999999', '-', 'causal (as reconstructed)'),
                                      ('sig_causal', True, '#ff7f50', '--', r'causal, $\kappa\to-\kappa$ (paper)'),
                                      ('sig_acausal', False, '#1b9e77', ':', 'acausal (reflected SV)')]:
            k, w = vertices(S[s], 'os', stage, kv, flip)
            h, _ = np.histogram(np.clip(k, -149.99, 149.99), bins, weights=w)
            n = h.sum()
            ax.step(bins, np.append(h, h[-1]) / max(n, 1), where='post', color=col, ls=ls, lw=1.8, label='%s (N=%d)' % (lab, n))
            npos = float((k > 0).sum()); nneg = float((k < 0).sum())
            out[lab] = dict(N=int(len(k)), A=(npos - nneg) / max(npos + nneg, 1), median=float(np.median(k)) if len(k) else None,
                            frac_neg=nneg / max(npos + nneg, 1))
        ax.set_xlabel(r'$\kappa_\parallel$ (mm$\cdot$GeV)'); ax.set_ylabel('fraction of vertices / bin')
        ax.set_title('signal M=200 GeV, Z-only — stage %s, P_tot=%s' % (stage.upper(), kv), fontsize=9)
        ax.legend(fontsize=8, frameon=False); ax.set_xlim(-150, 150)
        fig.savefig(os.path.join(PLOTS, 'signal_flip_vs_reflect_%s_%s.png' % (stage, kv)), dpi=150, bbox_inches='tight')
        plt.close(fig)
        res['%s_%s' % (stage, kv)] = out
for s in S:
    res['cutflow_' + s] = dict(os=S[s]['cos'].tolist(), ss=S[s]['css'].tolist())
    ev = S[s]['ev']
    # reconstructed vs generated: transverse displacement of gen electrons from W/Z/LW parents
    res['nevents_tree_' + s] = len(ev)
json.dump(res, open(os.path.join(PLOTS, 'signal_flip_vs_reflect.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
