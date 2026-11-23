#!/usr/bin/env python3
"""Hypothesis test: thesis L_T cut 0.02 applied in cm (CMSSW units) = 0.2 mm."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_v2 import load
import numpy as np, awkward as ak
out = {}
for thr in [0.02, 0.2]:
    for s in ['data', 'DY', 'TT', 'sig_causal', 'sig_acausal']:
        d = load(s); e = d['ev']; e = e[e.isOS == 1]
        flip = s == 'sig_causal'
        k = ak.where((e.sv_sig == 1) & flip, -e.sv_k, e.sv_k)
        cand = (k < 0) & (e.sv_ptT > 20)
        lt = e.sv_LT > thr
        n = len(e); A = np.zeros(n, bool)
        for kk in [0, 1]:
            m = e.sv_ele == kk
            km, cm, lm = k[m], cand[m], lt[m]
            for i in range(n):
                c = ak.to_numpy(cm[i]); l = ak.to_numpy(lm[i])
                for v in np.where(c)[0]:
                    if np.all(np.delete(l, v)): A[i] = True; break
        out['%s_thr%g' % (s, thr)] = dict(eff=float(A.mean()), N=n, frac_SV_LT_gt=float(ak.mean(ak.flatten(lt))))
print(json.dumps(out, indent=1)); json.dump(out, open('plots/ipp_units.json', 'w'), indent=1)
