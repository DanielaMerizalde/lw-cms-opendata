#!/usr/bin/env python3
"""Signal diagnostics for RESULTS.md: truth sign conventions, SV-truth matching, IPP, causal vs acausal."""
import glob, os, json
import numpy as np, uproot, awkward as ak
HERE = os.path.dirname(os.path.abspath(__file__))
res = {}
def files(s): return sorted(glob.glob(os.path.join(HERE, 'out', s, '*.root')))
# (3) per-block cutflow on common blocks
cf = {}
for s in ['sig_causal', 'sig_acausal']:
    for f in files(s):
        b = f.split('_')[-2]
        cf.setdefault(b, {})[s] = uproot.open(f)['wdv/cutflow_os'].values().astype(int).tolist()
common = [b for b in cf if len(cf[b]) == 2]
tot = {s: np.sum([cf[b][s] for b in common], axis=0).tolist() for s in ['sig_causal', 'sig_acausal']}
res['cutflow_common_blocks'] = dict(blocks=len(common), **tot)
# event overlap at DRC
ev = {}
for s in ['sig_causal', 'sig_acausal']:
    arrs = []
    for f in files(s):
        b = f.split('_')[-2]
        if b not in common: continue
        t = uproot.open(f)['wdv/events'].arrays()
        t['blk'] = int(b[1:])
        arrs.append(t)
    ev[s] = ak.concatenate(arrs)
keys = {s: set(zip(ak.to_list(ev[s].blk), ak.to_list(ev[s].event))) for s in ev}
res['DRC_events'] = {s: len(keys[s]) for s in keys}
res['DRC_events_in_both'] = len(keys['sig_causal'] & keys['sig_acausal'])
res['event_numbers_example'] = {s: sorted(list(keys[s]))[:5] for s in keys}

def truth(s):
    e = ev[s]; e = e[e.isOS == 1]
    out = dict(kgen=[], dgen=[], match=[], kmatched=[], kall=[], dist=[], ipp=[], nsv=[], kfirst=[])
    for i in range(len(e)):
        x = e[i]
        pv = np.array([x.pvx, x.pvy])
        for k in range(len(x.e_pt)):
            if not x.e_sig[k]: continue
            # gen electron matched to this reco electron
            gi = [j for j in range(len(x.g_pt)) if abs(x.g_mid[j]) == 9000011 and
                  np.hypot(x.g_eta[j] - x.e_eta[k], (x.g_phi[j] - x.e_phi[k] + np.pi) % (2 * np.pi) - np.pi) < 0.1]
            if not gi: continue
            g = gi[0]
            gv = np.array([x.g_vx[g], x.g_vy[g]])
            pT = x.g_pt[g] * np.array([np.cos(x.g_phi[g]), np.sin(x.g_phi[g])])
            d = (gv - pv) * 10  # mm
            out['kgen'].append(float(d @ pT)); out['dgen'].append(float(np.hypot(*d)))
            svs = [v for v in range(len(x.sv_k)) if x.sv_ele[v] == k and x.sv_LT[v] > 0.02]
            out['nsv'].append(len([v for v in range(len(x.sv_k)) if x.sv_ele[v] == k]))
            for v in svs:
                sv = np.array([x.sv_x[v], x.sv_y[v]])
                dist = float(np.hypot(*(sv - gv)) * 10)
                out['dist'].append(dist)
                m = dist < 0.5 * max(np.hypot(*d), 1e-6)   # SV closer to the true decay point than half the true displacement
                out['match'].append(m)
                out['kall'].append(float(x.sv_k[v]))
                if m: out['kmatched'].append(float(x.sv_k[v]))
    return out
for s in ['sig_causal', 'sig_acausal']:
    o = truth(s)
    kg = np.array(o['kgen']); dg = np.array(o['dgen']); km = np.array(o['kmatched']); ka = np.array(o['kall'])
    def nf(a): return [float((a < 0).mean()), float(np.sqrt((a < 0).mean() * (1 - (a < 0).mean()) / max(len(a), 1))), len(a)] if len(a) else None
    res[s] = dict(
        truth_kappa_negfrac=nf(kg),
        truth_LT_mm_quantiles=np.percentile(dg, [25, 50, 75]).round(4).tolist(),
        sv_minus_truth_dist_mm_quantiles=np.percentile(o['dist'], [25, 50, 75]).round(4).tolist() if o['dist'] else None,
        frac_SV_truth_matched=float(np.mean(o['match'])) if o['match'] else None,
        reco_kappa_negfrac_all=nf(ka), reco_kappa_negfrac_truthmatched=nf(km),
        nSV_per_signal_electron_mean=float(np.mean(o['nsv'])))
json.dump(res, open(os.path.join(HERE, 'plots', 'signal_investigation.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
