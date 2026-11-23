#!/usr/bin/env python3
"""hepmc_vertex_check.py -- verify, directly on the HepMC2 files, that the LW decay vertex
displacement is propagated to all descendants, and that the acausal file is the exact reflection
of the causal one.

  python3 hepmc_vertex_check.py causal.hepmc[.gz] [acausal.hepmc[.gz]] [--max N]

Per LW decay (bottom copy of |pdg| = 9000011):
  SV   = end vertex of the bottom copy, PV = production vertex of the top copy;
  final-state (status 1) descendants are classified by their production vertex:
     at_SV      : exactly at SV (|dx| < 1e-9 mm)
     further    : displaced further by a later decay (pi0/eta Dalitz ~nm, tau, D, B, ...)
     at_PV      : at the origin / PV  -> would be a bug
  For every vertex below SV we also check causality of the downstream step: it must lie downstream
  of the mother's production vertex along the mother momentum, (v - v_mother_prod).p_mother > 0.
  Steps with |d| < 1e-5 mm (10 nm) violating this are counted separately as back_tiny (Pythia parton ->
  string-copy bookkeeping, <= 5 nm, physically irrelevant); 'back' (>= 10 nm) must be 0.
  kappa_true = (SV - PV).p_LW  (> 0 causal, < 0 acausal).
With two files: same number of particles/vertices per event, identical P lines, and
SV_acausal = 2 PV - SV_causal for every LW decay; non-LW vertices unchanged.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hepmc2io import read_events  # noqa: E402

TOL = 1e-9


def dist(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def analyse(ev):
    out = []
    for top, bot in ev.lw_chains():
        pv = ev.vertices[top.prod].pos if top.prod in ev.vertices else [0, 0, 0, 0]
        sv = ev.vertices[bot.end].pos
        down = ev.descendant_vertices(bot.end)
        c = dict(at_SV=0, further=0, at_PV=0, back=0, back_tiny=0, back_maxd=0.0)
        for v in down:
            for pbc in ev.vertices[v].pout:
                p = ev.particles[pbc]
                if p.status != 1:
                    continue
                x = ev.vertices[v].pos
                if dist(x, sv) < TOL:
                    c['at_SV'] += 1
                elif dist(x, pv) < 1e-12:
                    c['at_PV'] += 1
                else:
                    c['further'] += 1
        # causality of downstream decays: each vertex below SV vs. the production vertex of its mother
        for v in down:
            if v == bot.end:
                continue
            for pbc in ev.vertices[v].pin:
                m = ev.particles[pbc]
                if m.prod is None:
                    continue
                d = [ev.vertices[v].pos[i] - ev.vertices[m.prod].pos[i] for i in range(3)]
                ad = sum(d[i] ** 2 for i in range(3)) ** 0.5
                if ad > 1e-12 and sum(d[i] * m.p[i] for i in range(3)) < 0:
                    # sub-nm "backward" steps occur in Pythia's parton -> string-copy bookkeeping
                    # (common offset of a whole Z->qq parton system, |d| <~ 5e-6 mm = 5 nm); they are irrelevant (CMS resolution ~ 2e-2 mm) and counted apart
                    if ad < 1e-5:
                        c['back_tiny'] += 1
                    else:
                        c['back'] += 1
                    c['back_maxd'] = max(c['back_maxd'], ad)
        kap = sum((sv[i] - pv[i]) * bot.p[i] for i in range(3))
        out.append(dict(pv=pv, sv=sv, kappa=kap, pdg=bot.pdg, **c))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('causal')
    ap.add_argument('acausal', nargs='?')
    ap.add_argument('--max', type=int, default=-1)
    a = ap.parse_args()
    it1 = read_events(a.causal)
    it2 = read_events(a.acausal) if a.acausal else None
    S = dict(events=0, lw=0, at_SV=0, further=0, at_PV=0, back=0, back_tiny=0, back_maxd=0.0, kpos=0, kneg=0,
             nonzeroPV=0)
    S2 = dict(lw=0, at_SV=0, further=0, at_PV=0, back=0, back_tiny=0, back_maxd=0.0, kpos=0, kneg=0, refl_ok=0,
              refl_bad=0,
              p_lines_diff=0, nonlw_vtx_moved=0)
    for (h1, e1) in it1:
        e2 = None
        if it2 is not None:
            h2, e2 = next(it2)
        if e1 is None:
            break
        if a.max >= 0 and S['events'] >= a.max:
            break
        S['events'] += 1
        r1 = analyse(e1)
        for r in r1:
            S['lw'] += 1
            for k in ('at_SV', 'further', 'at_PV', 'back', 'back_tiny'):
                S[k] += r[k]
            S['back_maxd'] = max(S['back_maxd'], r['back_maxd'])
            S['kpos' if r['kappa'] > 0 else 'kneg'] += 1
            if dist(r['pv'], [0, 0, 0]) > 1e-12:
                S['nonzeroPV'] += 1
        if e2 is not None:
            r2 = analyse(e2)
            for r, rc in zip(r2, r1):
                S2['lw'] += 1
                for k in ('at_SV', 'further', 'at_PV', 'back', 'back_tiny'):
                    S2[k] += r[k]
                S2['back_maxd'] = max(S2['back_maxd'], r['back_maxd'])
                S2['kpos' if r['kappa'] > 0 else 'kneg'] += 1
                exp = [2 * rc['pv'][i] - rc['sv'][i] for i in range(3)]
                S2['refl_ok' if dist(exp, r['sv']) < 1e-9 else 'refl_bad'] += 1
            pl1 = [l for l in e1.lines if l[0] == 'P']
            pl2 = [l for l in e2.lines if l[0] == 'P']
            S2['p_lines_diff'] += sum(x != y for x, y in zip(pl1, pl2)) + abs(len(pl1) - len(pl2))
            lwv = set()
            for top, bot in e1.lw_chains():
                lwv |= e1.descendant_vertices(bot.end)
            for bc, v in e1.vertices.items():
                if bc not in lwv and dist(v.pos, e2.vertices[bc].pos) > 0:
                    S2['nonlw_vtx_moved'] += 1
    print('CAUSAL  :', S)
    if it2 is not None:
        print('ACAUSAL :', S2)
    bad = S['at_PV'] or S['back'] or (it2 is not None and (S2['refl_bad'] or S2['p_lines_diff'] or S2['nonlw_vtx_moved']))
    print('RESULT  :', 'FAIL' if bad else 'PASS')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
