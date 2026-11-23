#!/usr/bin/env python3
"""Problem 3: which reading of the thesis selection reproduces its numbers?

Uses the v2 ntuples (out/<sample>/*.root; thesis selection up to SG, SVRA + Table 2.1, duplicates removed).
Every hypothesis is a rule that keeps a subset of the stored SVs (and optionally changes the L_T cut).
Two targets, both taken from the thesis:
  (1) SVs per SG event with L_T > 0.02 mm (Fig. 2.5 / paper Fig. 2): ~2300 / 48857 = 0.047
  (2) IPP efficiency relative to SG (Table 2.2): data 144/48857, LW200 0.02436/10.4, DY 10.6/31849, TT 22.5/2740
Signal uses the causal sample with the thesis flip (kappa -> -kappa for truth-matched electrons).
Usage: .venv/bin/python hypotheses_p3.py
"""
import glob, os, json
import numpy as np, uproot, awkward as ak

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_SV = 2300 / 48857
TARGET_IPP = {'data': 144 / 48857, 'sig_causal': 0.02436 / 10.4, 'DY': 10.6 / 31849, 'TT': 22.5 / 2740}

def load(s):
    ev = []
    for f in sorted(glob.glob(os.path.join(HERE, os.environ.get('P3_OUT', 'out'), s, '*.root'))):
        ev += ak.to_list(uproot.open(f)['wdv/events'].arrays(filter_name=['isOS', 'e_sig', 'sv_*']))
    return [e for e in ev if e['isOS'] == 1]

def best_by(e, idx, key):
    if not idx: return []
    if key == 'ntrk': return [max(idx, key=lambda v: (e['sv_ntrk'][v], -e['sv_chi2ndf'][v]))]
    if key == 'chi2': return [min(idx, key=lambda v: e['sv_chi2ndf'][v])]
    if key == 'LTsig': return [max(idx, key=lambda v: e['sv_LTsig'][v])]

def per_ele(e, key):
    out = []
    for k in (0, 1): out += best_by(e, [v for v in range(len(e['sv_k'])) if e['sv_ele'][v] == k], key)
    return out

# hypothesis -> (rule selecting SV indices, L_T threshold in mm)
H = {
    'v2 tal cual':                           (lambda e: list(range(len(e['sv_k']))), 0.02),
    'L_T en cm (0.2 mm)':                    (lambda e: list(range(len(e['sv_k']))), 0.2),
    '|P_T| > 20 GeV también en la figura':   (lambda e: [v for v in range(len(e['sv_k'])) if e['sv_ptT'][v] > 20], 0.02),
    '1 SV por electrón (más trazas)':        (lambda e: per_ele(e, 'ntrk'), 0.02),
    '1 SV por electrón (mejor χ²)':          (lambda e: per_ele(e, 'chi2'), 0.02),
    '1 SV por colisión (más trazas)':        (lambda e: best_by(e, list(range(len(e['sv_k']))), 'ntrk'), 0.02),
    'L_T/σ > 3':                             (lambda e: [v for v in range(len(e['sv_k'])) if e['sv_LTsig'][v] > 3], 0.02),
    '≥ 8 trazas':                            (lambda e: [v for v in range(len(e['sv_k'])) if e['sv_ntrk'][v] >= 8], 0.02),
    '1 SV por electrón + L_T en cm':         (lambda e: per_ele(e, 'ntrk'), 0.2),
    '1 SV por colisión + |P_T| > 20':        (lambda e: best_by(e, [v for v in range(len(e['sv_k'])) if e['sv_ptT'][v] > 20], 'ntrk'), 0.02),
}

def evaluate(evs, rule, lt, flip):
    nsv, nipp = 0, 0
    for e in evs:
        keep = rule(e)
        nsv += sum(1 for v in keep if e['sv_LT'][v] > lt)
        ipp = False
        for k in (0, 1):
            sgn = -1. if (flip and e['e_sig'][k]) else 1.
            mine = [v for v in keep if e['sv_ele'][v] == k]
            for v in mine:
                if sgn * e['sv_k'][v] < 0 and e['sv_ptT'][v] > 20 and all(e['sv_LT'][u] > lt for u in mine if u != v):
                    ipp = True; break
        nipp += ipp
    n = len(evs)
    return dict(n_SG=n, sv_per_event=nsv / n if n else None, ipp_eff=nipp / n if n else None, n_ipp=nipp)

S = {s: load(s) for s in ['data', 'sig_causal', 'DY', 'TT']}
res = {}
for name, (rule, lt) in H.items():
    res[name] = {s: evaluate(evs, rule, lt, flip=(s == 'sig_causal')) for s, evs in S.items()}
json.dump(dict(targets=dict(sv_per_event=TARGET_SV, ipp=TARGET_IPP), results=res),
          open(os.path.join(HERE, 'plots', 'hypotheses_p3.json'), 'w'), indent=1, ensure_ascii=False)
print('SG events:', {s: len(v) for s, v in S.items()})
print('%-38s %10s %10s %10s %10s %10s' % ('hipótesis', 'SV/ev dat', 'IPP dat', 'IPP señal', 'IPP DY', 'IPP TT'))
print('%-38s %10.3f %10.4f %10.4f %10.5f %10.4f' % ('META (tesis)', TARGET_SV, TARGET_IPP['data'], TARGET_IPP['sig_causal'], TARGET_IPP['DY'], TARGET_IPP['TT']))
for name, r in res.items():
    print('%-38s %10.3f %10.4f %10.4f %10.5f %10.4f' % (name, r['data']['sv_per_event'], r['data']['ipp_eff'], r['sig_causal']['ipp_eff'], r['DY']['ipp_eff'], r['TT']['ipp_eff']))
