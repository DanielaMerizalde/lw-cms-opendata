#!/usr/bin/env python3
"""IPP variants evaluated on the ntuples (SG stage, OS) to understand the thesis' tiny IPP efficiency."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_v2 import load
import numpy as np, awkward as ak
out = {}
for s in ['data', 'DY', 'TT', 'sig_causal', 'sig_acausal']:
    d = load(s); e = d['ev']; e = e[e.isOS == 1]
    flip = s == 'sig_causal'
    k = ak.where((e.sv_sig == 1) & flip, -e.sv_k, e.sv_k)
    cand = (k < 0) & (e.sv_ptT > 20)
    lt = e.sv_LT > 0.02
    n = len(e)
    # A: ours (per electron, all OTHER SVs of that electron with LT>0.02)
    A = e.passIPPflip if flip else e.passIPP
    # B: per electron, ALL SVs of that electron (incl. candidate) with LT>0.02
    B = np.zeros(n, bool); C = np.zeros(n, bool)
    for kk in [0, 1]:
        m = e.sv_ele == kk
        allok = ak.all(lt[m], axis=1) & (ak.num(e.sv_k[m]) > 0)
        B = B | ak.to_numpy(allok & ak.any(cand[m], axis=1))
    # C: all SVs in the event with LT>0.02 and one candidate
    C = ak.to_numpy(ak.all(lt, axis=1) & ak.any(cand, axis=1))
    nsv = ak.to_numpy(ak.num(e.sv_k))
    out[s] = dict(N_SG=n, mean_nSV_event=float(nsv.mean()) if n else None,
                  eff_ours=float(ak.sum(A) / n), eff_allSVofElectron=float(B.sum() / n), eff_allSVinEvent=float(C.sum() / n),
                  frac_SV_LT_gt_0p02=float(ak.mean(ak.flatten(lt))) if n else None)
print(json.dumps(out, indent=1))
json.dump(out, open('plots/ipp_variants.json', 'w'), indent=1)
