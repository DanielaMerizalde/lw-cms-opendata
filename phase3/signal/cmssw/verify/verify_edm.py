#!/usr/bin/env python
"""verify_edm.py -- phase-3A vertex verification on CMSSW EDM files (run inside the CMSSW_5_3_32 container, python2/FWLite).

  python verify_edm.py --gensim gensim.root [--aod aod.root] --truth truth_M200_elw.csv --out out.csv [--max N]

For every LW particle (|pdg| = 9000011, last copy = the one whose daughters are not LW):
  PV  = production vertex of the first LW copy (genParticles, after VtxSmeared; units cm)
  SV  = production vertex of the LW daughter electron (genParticles)
  truth (original HepMC, before smearing): SV0 - PV0 = (xd-xp, yd-yp, zd-zp) mm from the Pythia truth CSV
  (a) gen check : (SV - PV)_gen  ==  (SV0 - PV0)_HepMC        -> internal offsets survive MCFileSource+VtxSmeared
  (b) G4 check  : SimTrack of the electron (momentum match) starts at SimVertex == SV
  (c) RECO      : gsfElectron / generalTrack matched in dR to the gen electron: d_xy w.r.t. the true PV and
                  the reconstructed PV, compared with the true d_xy of a straight line from SV (CMS sign convention
                  dxy = (-(x-x0) py + (y-y0) px)/pT).
"""
import optparse
import csv
import math
import sys

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load('libFWCoreFWLite')
ROOT.AutoLibraryLoader.enable()
from DataFormats.FWLite import Events, Handle  # noqa: E402

LW = 9000011
ap = optparse.OptionParser()
ap.add_option('--gensim')
ap.add_option('--aod')
ap.add_option('--truth')
ap.add_option('--out')
ap.add_option('--max', type='int', default=-1)
a, _ = ap.parse_args()

# truth CSV (one row per LW, iev 0-based == EventID.event - 1)
truth = {}
for r in csv.DictReader(open(a.truth)):
    truth.setdefault(int(r['iev']), []).append(r)


def lw_rows(ev, gp):
    """return list of dicts per LW decay from genParticles"""
    out = []
    for i in range(gp.size()):
        p = gp.at(i)
        if abs(p.pdgId()) != LW:
            continue
        # last copy: no LW daughter
        nd = p.numberOfDaughters()
        if nd == 0 or any(abs(p.daughter(k).pdgId()) == LW for k in range(nd)):
            continue
        ele = None
        for k in range(nd):
            d = p.daughter(k)
            if abs(d.pdgId()) == 11:
                ele = d
        if ele is None:
            continue
        top = p
        while top.numberOfMothers() > 0 and abs(top.mother(0).pdgId()) == LW:
            top = top.mother(0)
        out.append(dict(pdg=p.pdgId(), px=p.px(), py=p.py(), pz=p.pz(),
                        PV=(top.vx(), top.vy(), top.vz()), SV=(ele.vx(), ele.vy(), ele.vz()),
                        e=ele))
    return out


def follow_final_e(e):
    """follow the electron through QED FSR copies to the last (status 1) copy"""
    while e.status() != 1:
        nxt = None
        for k in range(e.numberOfDaughters()):
            if e.daughter(k).pdgId() == e.pdgId():
                nxt = e.daughter(k)
        if nxt is None:
            break
        e = nxt
    return e


def dxy(x, y, px, py, x0, y0):
    return (-(x - x0) * py + (y - y0) * px) / math.hypot(px, py)


def dR(eta1, phi1, eta2, phi2):
    dphi = math.atan2(math.sin(phi1 - phi2), math.cos(phi1 - phi2))
    return math.hypot(eta1 - eta2, dphi)


hgp = Handle('std::vector<reco::GenParticle>')
hst = Handle('std::vector<SimTrack>')
hsv = Handle('std::vector<SimVertex>')
rows = {}
n = 0
for ev in Events(a.gensim):
    if 0 <= a.max <= n:
        break
    n += 1
    iev = ev.eventAuxiliary().event() - 1
    ev.getByLabel('genParticles', hgp)
    ev.getByLabel('g4SimHits', hst)
    ev.getByLabel('g4SimHits', hsv)
    gp, st, sv = hgp.product(), hst.product(), hsv.product()
    for L in lw_rows(ev, gp):
        t = [r for r in truth[iev] if int(r['id']) == L['pdg']][0]
        d0 = [float(t['xd']) - float(t['xp']), float(t['yd']) - float(t['yp']), float(t['zd']) - float(t['zp'])]  # mm
        dg = [10.0 * (L['SV'][k] - L['PV'][k]) for k in range(3)]  # mm
        ef = follow_final_e(L['e'])
        e0 = L['e']
        # G4: SimTrack with the same momentum as the (final) electron
        best, bdp = None, 1e9
        for j in range(st.size()):
            s = st.at(j)
            if abs(s.type()) != 11 or s.noGenpart():
                continue
            m = s.momentum()
            dp = abs(m.px() - ef.px()) + abs(m.py() - ef.py()) + abs(m.pz() - ef.pz())
            if dp < bdp:
                best, bdp = s, dp
        g4 = (float('nan'),) * 3
        if best is not None and bdp < 1e-3 and best.vertIndex() >= 0:
            v = sv.at(best.vertIndex()).position()
            g4 = (v.x(), v.y(), v.z())
        key = (iev, L['pdg'])
        rows[key] = dict(iev=iev, pdg=L['pdg'],
                         PVx=L['PV'][0], PVy=L['PV'][1], PVz=L['PV'][2],
                         SVx=L['SV'][0], SVy=L['SV'][1], SVz=L['SV'][2],
                         efx=ef.vx(), efy=ef.vy(), efz=ef.vz(),
                         dgen_minus_truth_mm=max(abs(dg[k] - d0[k]) for k in range(3)),
                         LT_truth_um=1e3 * math.hypot(d0[0], d0[1]),
                         g4_minus_SV_um=(1e4 * max(abs(g4[k] - L['SV'][k]) for k in range(3))
                                         if not math.isnan(g4[0]) else float('nan')),
                         efinal_minus_SV_um=1e4 * max(abs(v - s) for v, s in zip((ef.vx(), ef.vy(), ef.vz()), L['SV'])),
                         g4_dp=bdp,
                         e_pt=ef.pt(), e_eta=ef.eta(), e_phi=ef.phi(),
                         dxy_true_PV_um=1e4 * dxy(ef.vx(), ef.vy(), ef.px(), ef.py(), L['PV'][0], L['PV'][1]),
                         e0_status=e0.status())

if a.aod:
    hel = Handle('std::vector<reco::GsfElectron>')
    htr = Handle('std::vector<reco::Track>')
    hpv = Handle('std::vector<reco::Vertex>')
    hbs = Handle('reco::BeamSpot')
    for ev in Events(a.aod):
        iev = ev.eventAuxiliary().event() - 1
        ev.getByLabel('gsfElectrons', hel)
        ev.getByLabel('generalTracks', htr)
        ev.getByLabel('offlinePrimaryVertices', hpv)
        ev.getByLabel('offlineBeamSpot', hbs)
        els, trs, pvs, bs = hel.product(), htr.product(), hpv.product(), hbs.product()
        pv0 = pvs.at(0).position() if pvs.size() > 0 else None
        for key, r in rows.items():
            if key[0] != iev:
                continue
            r['bsx'], r['bsy'] = bs.x0(), bs.y0()
            r['npv'] = pvs.size()
            if pv0 is not None:
                r['recoPV_minus_truePV_um'] = 1e4 * math.sqrt((pv0.x() - r['PVx']) ** 2 + (pv0.y() - r['PVy']) ** 2 + (pv0.z() - r['PVz']) ** 2)
            for coll, tag in ((els, 'gsf'), (trs, 'trk')):
                best, bdr = None, 0.05
                for j in range(coll.size()):
                    o = coll.at(j)
                    if tag == 'gsf' and o.charge() * r['pdg'] > 0:  # e- from elw- (pdg>0): charge -1
                        pass
                    d = dR(o.eta(), o.phi(), r['e_eta'], r['e_phi'])
                    if d < bdr:
                        best, bdr = o, d
                if best is None:
                    continue
                t = best.gsfTrack() if tag == 'gsf' else best
                r[tag + '_pt'] = best.pt()
                r[tag + '_dR'] = bdr
                # dxy w.r.t. the true (smeared) PV, the reconstructed PV and the beamspot
                pt0 = ROOT.reco.Track.Point(r['PVx'], r['PVy'], r['PVz'])
                r[tag + '_dxy_truePV_um'] = 1e4 * t.dxy(pt0)
                if pv0 is not None:
                    r[tag + '_dxy_recoPV_um'] = 1e4 * t.dxy(pv0)
                r[tag + '_dxy_bs_um'] = 1e4 * t.dxy(bs.position())
                r[tag + '_dxyErr_um'] = 1e4 * t.dxyError()
                r[tag + '_nPixHits'] = t.hitPattern().numberOfValidPixelHits()

keys = []
for r in rows.values():
    for k in r:
        if k not in keys:
            keys.append(k)
w = csv.DictWriter(open(a.out, 'w'), fieldnames=keys)
w.writerow(dict(zip(keys, keys)))
for k in sorted(rows):
    w.writerow(rows[k])
print('wrote %d LW rows to %s' % (len(rows), a.out))
