#!/usr/bin/env python3
"""lw_reflect_hepmc.py -- make the ACAUSAL ("wrong displaced vertex", WDV) version of a HepMC2 file.

Physics (Alvarez, Da Rold, Schat, Szynkman, arXiv:0908.2446, Eq. 1; Grinstein, O'Connell, Wise,
arXiv:0805.2156): the decay products of a Lee-Wick resonance emerge from a vertex displaced
OPPOSITE to their total momentum, with the same exponential law (decay length beta*gamma*c*tau0).
Starting from a causal simulation, in which the LW particle produced at PV decays at
SV = PV + beta*gamma*c*tau * p_hat, the acausal event is obtained by reflecting the displacement
through the production vertex:

        SV' = PV - (SV - PV) = 2 PV - SV,     i.e.  shift  Delta = -2 (SV - PV)

and applying the SAME shift Delta to every vertex downstream of SV (Z -> q q~ parton shower,
string fragmentation of the LW-decay system, hadron / tau decays such as B -> D X ...).
Downstream propagation is left causal (a B hadron produced at SV' still flies along its momentum),
which is the correct prescription: only the LW propagator is acausal.  Momenta are not touched,
so causal and acausal files contain the same events (common random numbers) and differ only in the
positions of the LW-decay vertices.  By default the time component is reflected as well
(t' = 2 t_PV - t_SV: the products appear "before" the LW is produced, |dt| ~ 0.1 ps); use
--time keep to leave times unchanged.

The "paper approach" (J. Sanchez, ACI 15(1) 2780 (2023)) instead keeps the causal events and flips
the sign of kappa_par = (SV - PV) . P_tot for the signal; at truth level both are identical for
kappa_par, they differ only once detector reconstruction (vertex fitting, geometric cuts relative
to the beamspot, track-PV association) is applied -- that is why this file exists (phase 3).

Safety checks (printed at the end, non-zero exit code on failure):
  * every LW chain is found (top copy -> bottom copy), SV = end vertex of the bottom copy;
  * a vertex downstream of two different LW decays, or with incoming particles that are not
    downstream of the SV (e.g. a string connecting LW-decay partons to the underlying event)
    is reported as "mixed"; mixed vertices are shifted by the shift of the LW decay they belong to
    (first found) and counted -- they should be 0 for colour-singlet Z -> q q~ (checked: 0);
  * PV must be the production vertex of the top copy (0 for Pythia without vertex spread).

Usage:
  python3 lw_reflect_hepmc.py in.hepmc[.gz] out.hepmc[.gz] [--time reflect|keep] [--pdg 9000011]
Works on Pythia8 HepMC2 output before CMSSW vertex smearing (beamspot is added afterwards by
VtxSmeared, which shifts all vertices rigidly and therefore preserves the reflection).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hepmc2io import read_events, _open  # noqa: E402


def fmt(x):
    return '%.10e' % x if x != 0 else '0'


def reflect_event(ev, pdg_abs=9000011, time_mode='reflect'):
    """Modify ev.lines in place. Returns dict with diagnostics."""
    chains = ev.lw_chains(pdg_abs)
    shift = {}            # vertex barcode -> (dx,dy,dz,dt)
    owner = {}
    n_mixed = 0
    info = []
    for top, bot in chains:
        k = len(info)
        pv = ev.vertices[top.prod].pos if top.prod in ev.vertices else [0, 0, 0, 0]
        if bot.end not in ev.vertices:
            continue
        sv = ev.vertices[bot.end].pos
        d = [-2.0 * (sv[i] - pv[i]) for i in range(3)]
        d.append(-2.0 * (sv[3] - pv[3]) if time_mode == 'reflect' else 0.0)
        down = ev.descendant_vertices(bot.end)
        for v in down:
            if v in shift:
                n_mixed += 1           # downstream of two LW decays
                continue
            shift[v], owner[v] = d, k
        info.append((top, bot, pv, sv, d, down))
    # vertices with incoming particles produced outside the LW-decay tree
    for v, k in owner.items():
        if v == info[k][1].end:
            continue
        for pbc in ev.vertices[v].pin:
            pr = ev.particles[pbc].prod
            if pr is None or owner.get(pr) != k:
                n_mixed += 1
                break
    for v, d in shift.items():
        vx = ev.vertices[v]
        f = ev.lines[vx.line].split()
        newpos = [vx.pos[i] + d[i] for i in range(4)]
        f[3:7] = [fmt(x) for x in newpos]
        ev.lines[vx.line] = ' '.join(f) + '\n'
        vx.pos = newpos
    return dict(n_lw=len(info), n_shifted=len(shift), n_mixed=n_mixed)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inp')
    ap.add_argument('out')
    ap.add_argument('--time', choices=['reflect', 'keep'], default='reflect')
    ap.add_argument('--pdg', type=int, default=9000011)
    a = ap.parse_args()
    tot = dict(events=0, n_lw=0, n_shifted=0, n_mixed=0, ev_without_2lw=0)
    with _open(a.out, 'wt') as fo:
        for header, ev in read_events(a.inp):
            fo.writelines(header)
            if ev is None:
                continue
            r = reflect_event(ev, a.pdg, a.time)
            tot['events'] += 1
            for k in ('n_lw', 'n_shifted', 'n_mixed'):
                tot[k] += r[k]
            if r['n_lw'] != 2:
                tot['ev_without_2lw'] += 1
            fo.writelines(ev.lines)
    print('lw_reflect_hepmc: %(events)d events, %(n_lw)d LW decays reflected, %(n_shifted)d vertices '
          'shifted, mixed=%(n_mixed)d, events without 2 LW=%(ev_without_2lw)d' % tot)
    sys.exit(1 if (tot['n_mixed'] or tot['ev_without_2lw']) else 0)


if __name__ == '__main__':
    main()
