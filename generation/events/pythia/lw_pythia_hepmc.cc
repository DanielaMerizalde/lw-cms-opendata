// lw_pythia_hepmc.cc -- Pythia 8.317 driver for the Lee-Wick electron signal (phase 2B).
//
//   LHE (MG5 decay chain, VTIMUP written)  ->  ISR/FSR/MPI/hadronisation (CUETP8M1)
//   -> HepMC2 (IO_GenEvent, GeV/mm; CMSSW_5_3 MCFileSource-compatible)
//   -> truth tables: <out>_elw.csv (one row per elw) and <out>_jets.csv (anti-kT 0.5 truth jets)
//
// Usage: lw_pythia_hepmc card.cmnd events.lhe[.gz] out_prefix M ctau0_mm seed [nEvents]
//
// Vertex bookkeeping checked per event and per elw (columns n_desc, n_atSV, n_atPV, n_further):
//   every final-state (status 1) descendant of an elw must have a production vertex either exactly at
//   the elw decay vertex SV, or displaced further from SV by a subsequent hadron/tau decay (n_further).
//   n_atPV counts descendants wrongly produced at the origin (must be 0).
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC2.h"
#include "HepMC/IO_GenEvent.h"
#include <fstream>
#include <set>
using namespace Pythia8;

// collect all descendants of i (any status)
static void descendants(const Event& ev, int i, std::set<int>& out) {
  for (int d : ev[i].daughterList()) if (d > 0 && !out.count(d)) { out.insert(d); descendants(ev, d, out); }
}
// follow copies (recoil copies AND photon/gluon emissions off the particle itself, e.g. QED FSR
// elw -> elw gamma) down to the bottom copy, which is the one that decays
static int lastCopy(const Event& ev, int i) { return ev[i].iBotCopyId(); }
// jet selection: visible final-state particles, excluding the two hard electrons from elw decays
class ExclHook : public SlowJetHook {
public:
  std::set<int> excl;
  bool include(int iSel, const Event& ev, Vec4&, double&) override {
    return ev[iSel].isFinal() && ev[iSel].isVisible() && !excl.count(iSel);
  }
};

int main(int argc, char* argv[]) {
  if (argc < 7) { std::cerr << "usage: card lhe out M ctau0_mm seed [nev]\n"; return 1; }
  std::string card = argv[1], lhe = argv[2], out = argv[3];
  double M = atof(argv[4]), ctau0 = atof(argv[5]);
  int seed = atoi(argv[6]); int nMax = (argc > 7) ? atoi(argv[7]) : -1;

  Pythia pythia;
  pythia.readFile(card);
  pythia.readString("Beams:LHEF = " + lhe);
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + std::to_string(seed));
  char buf[256];
  snprintf(buf, sizeof buf, "9000011:all = elw- elw+ 2 -3 0 %.6f 0. 0. 0. %.8g", M, ctau0);
  pythia.readString(buf);
  pythia.readString("9000011:mayDecay = off");
  if (!pythia.init()) return 2;

  HepMC::Pythia8ToHepMC toHepMC;
  toHepMC.set_print_inconsistency(true);
  HepMC::IO_GenEvent hepout(out + ".hepmc", std::ios::out);
  hepout.precision(10);   // 10 significant digits: ~1e-11 mm on 0.05 mm vertices; ~40% smaller files
  std::ofstream fe(out + "_elw.csv"), fj(out + "_jets.csv");
  fe << "iev,iw,id,px,py,pz,E,m,xp,yp,zp,tp,xd,yd,zd,td,tau,"
        "e_px,e_py,e_pz,e_E,ef_px,ef_py,ef_pz,ef_E,"
        "q1_id,q1_px,q1_py,q1_pz,q1_E,q2_id,q2_px,q2_py,q2_pz,q2_E,"
        "z_m,n_desc,n_atSV,n_atPV,n_further,max_off_mm\n";
  fj << "iev,ij,px,py,pz,E,f_w0,f_w1,nconst\n";
  fe.precision(9); fj.precision(7);

  ExclHook hook;
  SlowJet sj(-1, 0.5, 20., 4.7, 2, 2, &hook, true);  // anti-kT R=0.5, pT>20, |eta|<4.7 (E-scheme)

  long nBadPV = 0, nNonElwDisplaced = 0, nMixedHad = 0, nPrimHad = 0; int iev = 0, nFail = 0;
  while (nMax < 0 || iev < nMax) {
    if (!pythia.next()) {
      if (pythia.info.atEndOfFile()) break;
      if (++nFail > 100) break;
      continue;
    }
    Event& ev = pythia.event;
    if (getenv("LWDEBUG") && atoi(getenv("LWDEBUG")) == iev) { ev.list(false, false, 9); pythia.process.list(); }
    // --- HepMC
    HepMC::GenEvent* hev = new HepMC::GenEvent();
    toHepMC.fill_next_event(pythia, hev, iev);
    hepout << hev;
    delete hev;

    // --- truth: find the hard-process elw's (first copies) and follow to last copies
    std::vector<int> wFirst;
    for (int i = 0; i < ev.size(); ++i)
      if (ev[i].idAbs() == 9000011 && ev[ev[i].mother1()].idAbs() != 9000011) wFirst.push_back(i);
    std::set<int> allDesc[2];
    hook.excl.clear();
    std::vector<int> efinal(2, -1);
    for (size_t k = 0; k < wFirst.size() && k < 2; ++k) {
      int iw = lastCopy(ev, wFirst[k]);
      const Particle& w = ev[iw];
      Vec4 SV = w.vDec(), PV = ev[wFirst[k]].vProd();
      int ie = -1, iz = -1;
      for (int d : w.daughterList()) { if (ev[d].idAbs() == 11) ie = d; if (ev[d].id() == 23) iz = d; }
      // Z -> q qbar : last Z copy, its daughters (before FSR)
      int iz2 = (iz > 0) ? lastCopy(ev, iz) : -1;
      int q1 = -1, q2 = -1;
      if (iz2 > 0) { auto dl = ev[iz2].daughterList(); if (dl.size() >= 2) { q1 = dl[0]; q2 = dl[1]; } }
      // final electron: hardest final-state e with same id among descendants of ie
      std::set<int> ed; if (ie > 0) { ed.insert(ie); descendants(ev, ie, ed); }
      int ief = -1;
      for (int j : ed) if (ev[j].isFinal() && ev[j].id() == ev[ie].id() && (ief < 0 || ev[j].pT() > ev[ief].pT())) ief = j;
      efinal[k] = ief; if (ief > 0) hook.excl.insert(ief);
      // vertex checks over all final-state descendants
      std::set<int> desc; descendants(ev, iw, desc); allDesc[k] = desc;
      int nD = 0, nSV = 0, nPV = 0, nFur = 0; double maxOff = 0;
      for (int j : desc) {
        if (!ev[j].isFinal()) continue;
        ++nD;
        double off = (ev[j].vProd() - SV).pAbs();  // spatial part
        if (off < 1e-9) ++nSV;
        else if (ev[j].vProd().pAbs() < 1e-12) ++nPV;
        else { ++nFur; maxOff = std::max(maxOff, off); }
      }
      nBadPV += nPV;
      auto P4 = [&](int j) { char b[200]; if (j < 0) snprintf(b, sizeof b, "0,0,0,0");
        else snprintf(b, sizeof b, "%.6f,%.6f,%.6f,%.6f", ev[j].px(), ev[j].py(), ev[j].pz(), ev[j].e()); return std::string(b); };
      fe << iev << "," << k << "," << w.id() << "," << w.px() << "," << w.py() << "," << w.pz() << "," << w.e() << "," << w.m() << ","
         << PV.px() << "," << PV.py() << "," << PV.pz() << "," << PV.e() << ","
         << SV.px() << "," << SV.py() << "," << SV.pz() << "," << SV.e() << "," << w.tau() << ","
         << P4(ie) << "," << P4(ief) << ","
         << (q1 > 0 ? ev[q1].id() : 0) << "," << P4(q1) << "," << (q2 > 0 ? ev[q2].id() : 0) << "," << P4(q2) << ","
         << (iz2 > 0 ? ev[iz2].m() : 0.) << "," << nD << "," << nSV << "," << nPV << "," << nFur << "," << maxOff << "\n";
    }
    // non-elw final-state particles with displaced vertex not explained by a decayed hadron mother
    for (int i = 0; i < ev.size(); ++i) {
      if (!ev[i].isFinal() || allDesc[0].count(i) || allDesc[1].count(i)) continue;
      if (ev[i].vProd().pAbs() > 1e-12) {
        int m = ev[i].mother1();
        if (!(m > 0 && ev[m].isHadron() || (m > 0 && ev[m].idAbs() == 15))) ++nNonElwDisplaced;
      }
    }
    // strings/clusters mixing LW-decay partons with partons from elsewhere (other elw, ISR, MPI, remnant)
    for (int i = 0; i < ev.size(); ++i) {
      int st = ev[i].statusAbs();
      if (st < 81 || st > 89) continue;          // primary hadrons from string/ministring/cluster
      std::vector<int> ml = ev[i].motherList();
      int nIn0 = 0, nIn1 = 0, nOut = 0;
      for (int m : ml) { if (allDesc[0].count(m)) ++nIn0; else if (allDesc[1].count(m)) ++nIn1; else ++nOut; }
      if ((nIn0 > 0) + (nIn1 > 0) + (nOut > 0) > 1) ++nMixedHad;
      ++nPrimHad;
    }
    // --- truth jets
    sj.analyze(ev);
    for (int ij = 0; ij < sj.sizeJet() && ij < 10; ++ij) {
      Vec4 p = sj.p(ij); double f[2] = {0, 0}; double ptsum = 0;
      for (int c : sj.constituents(ij)) { ptsum += ev[c].pT(); for (int k = 0; k < 2; ++k) if (allDesc[k].count(c)) f[k] += ev[c].pT(); }
      fj << iev << "," << ij << "," << p.px() << "," << p.py() << "," << p.pz() << "," << p.e() << ","
         << f[0] / ptsum << "," << f[1] / ptsum << "," << sj.multiplicity(ij) << "\n";
    }
    ++iev;
  }
  pythia.stat();
  std::cout << "LWSUMMARY events=" << iev << " descendants_at_PV(bad)=" << nBadPV
            << " nonLW_displaced_unexplained=" << nNonElwDisplaced
            << " primary_hadrons=" << nPrimHad << " from_mixed_strings=" << nMixedHad << std::endl;
  return 0;
}
