// WDVv3Analyzer: improvements study (phase 3, "mejoras") on the simulated LW signal.
// Same trigger/object selection as WDVAnalyzer v2 (TF, TO, HQ, JetS), no DRC cut (stored as flag).
// For every electron x jet-pair candidate (50 < m_jj < 170 GeV) it stores the mass/boost variables,
// the truth assignment, and vertex fits for 4 track-cleaning settings x 3 fitters:
//   cleaning 0: none; 1: drop tracks with weight>0.5 in ANY offline vertex (signal PV or PU);
//            2: drop tracks with weight>0.5 in a PU vertex, or transverse IP significance wrt PV < 2;
//            3: as 2 with IP significance < 3.  (the electron track is always kept)
//   fitter 0: SVRA as v2 (pair seeds, merging, Table 2.1; all SVs containing the electron);
//   fitter 1: single Kalman fit of all tracks; fitter 2: single Adaptive fit of all tracks.
// Truth (signal): LW production vertex (= true PV), decay vertex, electron, Z quarks.
#include <memory>
#include <vector>
#include <string>
#include <set>
#include <map>
#include <algorithm>
#include <cmath>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "JetMETCorrections/Objects/interface/JetCorrector.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/AdaptiveVertexFit/interface/AdaptiveVertexFitter.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "TTree.h"
#include "TH1D.h"
#include "TLorentzVector.h"

namespace {
  struct SelJet { const reco::PFJet* jet; double pt, eta, phi, e, px, py, pz, emf; int nconst; bool good; };
  struct FitV { int id; std::vector<int> trk; reco::Vertex v; double chi2ndf; };
  bool byPt(const SelJet& a, const SelJet& b) { return a.pt > b.pt; }
  const reco::Candidate* lastCopy(const reco::Candidate* p) {
    for (int it = 0; it < 100; ++it) {
      const reco::Candidate* nx = 0;
      for (size_t i = 0; i < p->numberOfDaughters(); ++i) if (p->daughter(i)->pdgId() == p->pdgId()) nx = p->daughter(i);
      if (!nx) break;
      p = nx;
    }
    return p;
  }
}

class WDVv3Analyzer : public edm::EDAnalyzer {
public:
  explicit WDVv3Analyzer(const edm::ParameterSet&);
private:
  virtual void beginJob();
  virtual void beginRun(const edm::Run&, const edm::EventSetup&);
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  bool fitKVF(const std::vector<reco::TransientTrack>& tts, const std::vector<int>& idx, FitV& out, int& nextId, bool cut) const;
  std::vector<FitV> svra(const std::vector<reco::TransientTrack>& tts) const;

  std::vector<std::string> hltThesis_;
  std::string jecName_;
  bool isData_; std::vector<int> cleanings_, fitters_;
  float genW_; TH1D* hCutW_;
  int lwPdg_;
  HLTConfigProvider hltConfig_; bool hltOk_;
  TTree* tree_; TH1D* hCut_;

  unsigned run_; unsigned long long evt_;
  int isOS_, nPV_;
  float pvx_, pvy_, pvz_, pvcxx_, pvcxy_, pvcyy_;
  // truth (per LW, up to 2)
  std::vector<float> t_pvx_, t_pvy_, t_pvz_, t_dvx_, t_dvy_, t_dvz_, t_lpt_, t_leta_, t_lphi_, t_lm_;
  std::vector<float> t_ept_, t_eeta_, t_ephi_, t_q1pt_, t_q1eta_, t_q1phi_, t_q2pt_, t_q2eta_, t_q2phi_;
  std::vector<int> t_eq_;
  // reco electrons / jets
  std::vector<float> e_pt_, e_eta_, e_phi_, e_dR1_, e_dR2_; std::vector<int> e_q_, e_lw_, e_drc_;
  std::vector<float> j_pt_, j_eta_, j_phi_; std::vector<int> j_lw_;
  // candidates
  std::vector<int> c_ele_, c_j1_, c_j2_, c_truth_; std::vector<float> c_mjj_, c_mejj_, c_ptejj_, c_px_, c_py_, c_pz_;
  // fits
  std::vector<int> f_cand_, f_clean_, f_fitter_, f_rank_, f_ntrk_, f_t21_, f_hasEle_, f_nset_;
  std::vector<float> f_x_, f_y_, f_z_, f_cxx_, f_cxy_, f_cyy_, f_czz_, f_chi2_, f_ptx_, f_pty_, f_ptz_, f_eW_;
};

WDVv3Analyzer::WDVv3Analyzer(const edm::ParameterSet& p) :
  hltThesis_(p.getParameter<std::vector<std::string> >("hltThesis")),
  jecName_(p.getParameter<std::string>("jecName")),
  isData_(p.getParameter<bool>("isData")), cleanings_(p.getParameter<std::vector<int> >("cleanings")),
  fitters_(p.getParameter<std::vector<int> >("fitters")), lwPdg_(p.getParameter<int>("lwPdg")), hltOk_(false) {}

void WDVv3Analyzer::beginRun(const edm::Run& r, const edm::EventSetup& es) { bool ch = false; hltOk_ = hltConfig_.init(r, es, "HLT", ch); }

void WDVv3Analyzer::beginJob() {
  edm::Service<TFileService> fs;
  hCut_ = fs->make<TH1D>("cutflow", "NF TF TO HQ JetS OS", 6, 0, 6);
  hCutW_ = fs->make<TH1D>("cutflow_w", "NF TF TO HQ JetS OS (sum of gen-weight signs)", 6, 0, 6);
  tree_ = fs->make<TTree>("events", "v3 candidates and fits");
#define BR(x) tree_->Branch(#x, &x##_)
  tree_->Branch("run", &run_, "run/i"); tree_->Branch("event", &evt_, "event/l");
  tree_->Branch("isOS", &isOS_, "isOS/I"); tree_->Branch("genW", &genW_, "genW/F"); tree_->Branch("nPV", &nPV_, "nPV/I");
  tree_->Branch("pvx", &pvx_, "pvx/F"); tree_->Branch("pvy", &pvy_, "pvy/F"); tree_->Branch("pvz", &pvz_, "pvz/F");
  tree_->Branch("pvcxx", &pvcxx_, "pvcxx/F"); tree_->Branch("pvcxy", &pvcxy_, "pvcxy/F"); tree_->Branch("pvcyy", &pvcyy_, "pvcyy/F");
  BR(t_pvx); BR(t_pvy); BR(t_pvz); BR(t_dvx); BR(t_dvy); BR(t_dvz); BR(t_lpt); BR(t_leta); BR(t_lphi); BR(t_lm);
  BR(t_ept); BR(t_eeta); BR(t_ephi); BR(t_eq); BR(t_q1pt); BR(t_q1eta); BR(t_q1phi); BR(t_q2pt); BR(t_q2eta); BR(t_q2phi);
  BR(e_pt); BR(e_eta); BR(e_phi); BR(e_q); BR(e_lw); BR(e_drc); BR(e_dR1); BR(e_dR2);
  BR(j_pt); BR(j_eta); BR(j_phi); BR(j_lw);
  BR(c_ele); BR(c_j1); BR(c_j2); BR(c_truth); BR(c_mjj); BR(c_mejj); BR(c_ptejj); BR(c_px); BR(c_py); BR(c_pz);
  BR(f_cand); BR(f_clean); BR(f_fitter); BR(f_rank); BR(f_ntrk); BR(f_t21); BR(f_hasEle); BR(f_nset);
  BR(f_x); BR(f_y); BR(f_z); BR(f_cxx); BR(f_cxy); BR(f_cyy); BR(f_czz); BR(f_chi2); BR(f_ptx); BR(f_pty); BR(f_ptz); BR(f_eW);
#undef BR
}

bool WDVv3Analyzer::fitKVF(const std::vector<reco::TransientTrack>& tts, const std::vector<int>& idx, FitV& out, int& nextId, bool cut) const {
  if (idx.size() < 2) return false;
  std::vector<reco::TransientTrack> v;
  for (size_t i = 0; i < idx.size(); ++i) v.push_back(tts[idx[i]]);
  KalmanVertexFitter kvf(false);
  TransientVertex tv;
  try { tv = kvf.vertex(v); } catch (...) { return false; }
  if (!tv.isValid() || tv.degreesOfFreedom() <= 0) return false;
  double c = tv.totalChiSquared() / tv.degreesOfFreedom();
  if (cut && !(c < 5.)) return false;
  out.trk = idx; std::sort(out.trk.begin(), out.trk.end());
  out.v = reco::Vertex(tv); out.chi2ndf = c; out.id = nextId++;
  return true;
}

std::vector<FitV> WDVv3Analyzer::svra(const std::vector<reco::TransientTrack>& tts) const {
  std::vector<FitV> vs; int nextId = 0; int n = tts.size();
  for (int i = 0; i < n; ++i) for (int j = i+1; j < n; ++j) {
    std::vector<int> idx(2); idx[0] = i; idx[1] = j;
    FitV f; if (fitKVF(tts, idx, f, nextId, true)) vs.push_back(f);
  }
  VertexDistance3D vd; std::set<std::pair<int,int> > tried; bool again = true; int guard = 0;
  while (again && guard++ < 20000) {
    again = false;
    for (size_t a = 0; a < vs.size() && !again; ++a) for (size_t b = a+1; b < vs.size(); ++b) {
      std::pair<int,int> key(std::min(vs[a].id, vs[b].id), std::max(vs[a].id, vs[b].id));
      if (tried.count(key)) continue;
      std::vector<int> sh;
      std::set_intersection(vs[a].trk.begin(), vs[a].trk.end(), vs[b].trk.begin(), vs[b].trk.end(), std::back_inserter(sh));
      if (sh.empty()) continue;
      tried.insert(key);
      if (!(vd.distance(vs[a].v, vs[b].v).significance() < 4.)) continue;
      std::vector<int> uni;
      std::set_union(vs[a].trk.begin(), vs[a].trk.end(), vs[b].trk.begin(), vs[b].trk.end(), std::back_inserter(uni));
      FitV m; if (!fitKVF(tts, uni, m, nextId, true)) continue;
      vs.erase(vs.begin() + b); vs.erase(vs.begin() + a); vs.push_back(m); again = true; break;
    }
  }
  std::vector<FitV> out;
  for (size_t a = 0; a < vs.size(); ++a) {
    bool dup = false; for (size_t b = 0; b < out.size(); ++b) if (out[b].trk == vs[a].trk) dup = true;
    if (!dup) out.push_back(vs[a]);
  }
  return out;
}

void WDVv3Analyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  genW_ = 1.;
  if (!isData_) { edm::Handle<GenEventInfoProduct> gi; if (iEvent.getByLabel("generator", gi) && gi.isValid()) genW_ = gi->weight() >= 0 ? 1. : -1.; }
  { hCut_->Fill(0); hCutW_->Fill(0., double(genW_)); }
  // ---- TF (as v2)
  edm::Handle<edm::TriggerResults> trh; iEvent.getByLabel(edm::InputTag("TriggerResults", "", "HLT"), trh);
  std::vector<std::string> fired;
  if (trh.isValid()) {
    const edm::TriggerNames& tn = iEvent.triggerNames(*trh);
    for (unsigned i = 0; i < tn.size(); ++i) if (trh->accept(i))
      for (size_t k = 0; k < hltThesis_.size(); ++k) if (tn.triggerName(i).compare(0, hltThesis_[k].size(), hltThesis_[k]) == 0) fired.push_back(tn.triggerName(i));
  }
  if (fired.empty()) return;
  edm::Handle<reco::GsfElectronCollection> eles; iEvent.getByLabel("gsfElectrons", eles);
  int nE20 = 0; for (size_t i = 0; i < eles->size(); ++i) if ((*eles)[i].pt() > 20) ++nE20;
  if (nE20 < 2) return;
  edm::Handle<reco::PFJetCollection> jets; iEvent.getByLabel("ak5PFJets", jets);
  const JetCorrector* corr = JetCorrector::getJetCorrector(jecName_, iSetup);
  std::vector<SelJet> alljets; int nTF = 0;
  for (size_t i = 0; i < jets->size(); ++i) {
    const reco::PFJet& j = (*jets)[i]; double s = corr->correction(j, iEvent, iSetup);
    SelJet sj; sj.jet = &j; sj.pt = j.pt()*s; sj.eta = j.eta(); sj.phi = j.phi(); sj.e = j.energy()*s;
    sj.px = j.px()*s; sj.py = j.py()*s; sj.pz = j.pz()*s;
    sj.emf = j.chargedEmEnergyFraction() + j.neutralEmEnergyFraction(); sj.nconst = j.nConstituents();
    sj.good = sj.pt > 20 && std::fabs(sj.eta) < 2.5 && sj.nconst > 1 && j.neutralHadronEnergyFraction() < 0.9 &&
              j.neutralEmEnergyFraction() < 0.9 && j.muonEnergyFraction() < 0.8 && sj.emf < 0.6;
    if (sj.pt > 15) ++nTF;
    alljets.push_back(sj);
  }
  if (nTF < 4) return;
  { hCut_->Fill(1); hCutW_->Fill(1., double(genW_)); }
  // ---- TO (trigger-object matching, as v2)
  std::vector<int> toIdx;
  edm::Handle<trigger::TriggerEvent> tev; iEvent.getByLabel(edm::InputTag("hltTriggerSummaryAOD", "", "HLT"), tev);
  if (hltOk_ && tev.isValid()) {
    std::set<trigger::size_type> keys;
    for (size_t p = 0; p < fired.size(); ++p) {
      if (hltConfig_.triggerIndex(fired[p]) >= hltConfig_.size()) continue;
      const std::vector<std::string>& mods = hltConfig_.moduleLabels(fired[p]);
      for (int m = int(mods.size()) - 1; m >= 0; --m) {
        trigger::size_type fi = tev->filterIndex(edm::InputTag(mods[m], "", "HLT"));
        if (fi >= tev->sizeFilters()) continue;
        const trigger::Keys& ks = tev->filterKeys(fi); for (size_t k = 0; k < ks.size(); ++k) keys.insert(ks[k]);
        break;
      }
    }
    const trigger::TriggerObjectCollection& objs = tev->getObjects();
    std::vector<std::pair<double, trigger::size_type> > cand;
    for (std::set<trigger::size_type>::const_iterator k = keys.begin(); k != keys.end(); ++k) cand.push_back(std::make_pair(objs[*k].pt(), *k));
    std::sort(cand.rbegin(), cand.rend());
    std::vector<trigger::size_type> lead;
    for (size_t c = 0; c < cand.size() && lead.size() < 2; ++c) {
      bool dup = false;
      for (size_t l = 0; l < lead.size(); ++l) if (reco::deltaR(objs[lead[l]].eta(), objs[lead[l]].phi(), objs[cand[c].second].eta(), objs[cand[c].second].phi()) < 0.1) dup = true;
      if (!dup) lead.push_back(cand[c].second);
    }
    for (size_t l = 0; l < lead.size(); ++l) {
      int best = -1; double bdr = 0.2;
      for (size_t i = 0; i < eles->size(); ++i) {
        double dr = reco::deltaR(objs[lead[l]].eta(), objs[lead[l]].phi(), (*eles)[i].superCluster()->eta(), (*eles)[i].superCluster()->phi());
        if (dr < bdr && std::find(toIdx.begin(), toIdx.end(), (int)i) == toIdx.end()) { bdr = dr; best = i; }
      }
      if (best >= 0) toIdx.push_back(best);
    }
  }
  if (toIdx.size() < 2) return;
  const reco::GsfElectron* el[2] = {&(*eles)[toIdx[0]], &(*eles)[toIdx[1]]};
  if (el[1]->pt() > el[0]->pt()) std::swap(el[0], el[1]);
  if (el[0]->pt() < 40 || el[1]->pt() < 25 || std::fabs(el[0]->superCluster()->eta()) > 2.5 || std::fabs(el[1]->superCluster()->eta()) > 2.5) return;
  { hCut_->Fill(2); hCutW_->Fill(2., double(genW_)); }
  reco::TrackRef ctf[2];
  for (int k = 0; k < 2; ++k) { ctf[k] = el[k]->closestCtfTrackRef(); if (ctf[k].isNull() || !ctf[k]->quality(reco::TrackBase::highPurity)) return; }
  { hCut_->Fill(3); hCutW_->Fill(3., double(genW_)); }
  std::vector<SelJet> sj;
  for (size_t i = 0; i < alljets.size(); ++i) if (alljets[i].good) sj.push_back(alljets[i]);
  std::sort(sj.begin(), sj.end(), byPt);
  if (sj.size() < 4) return;
  { hCut_->Fill(4); hCutW_->Fill(4., double(genW_)); }
  isOS_ = el[0]->charge() * el[1]->charge() < 0;
  if (isOS_) { hCut_->Fill(5); hCutW_->Fill(5., double(genW_)); }
  run_ = iEvent.id().run(); evt_ = iEvent.id().event();

  // ---- clear
  t_pvx_.clear(); t_pvy_.clear(); t_pvz_.clear(); t_dvx_.clear(); t_dvy_.clear(); t_dvz_.clear(); t_lpt_.clear(); t_leta_.clear(); t_lphi_.clear(); t_lm_.clear();
  t_ept_.clear(); t_eeta_.clear(); t_ephi_.clear(); t_eq_.clear(); t_q1pt_.clear(); t_q1eta_.clear(); t_q1phi_.clear(); t_q2pt_.clear(); t_q2eta_.clear(); t_q2phi_.clear();
  e_pt_.clear(); e_eta_.clear(); e_phi_.clear(); e_q_.clear(); e_lw_.clear(); e_drc_.clear(); e_dR1_.clear(); e_dR2_.clear();
  j_pt_.clear(); j_eta_.clear(); j_phi_.clear(); j_lw_.clear();
  c_ele_.clear(); c_j1_.clear(); c_j2_.clear(); c_truth_.clear(); c_mjj_.clear(); c_mejj_.clear(); c_ptejj_.clear(); c_px_.clear(); c_py_.clear(); c_pz_.clear();
  f_cand_.clear(); f_clean_.clear(); f_fitter_.clear(); f_rank_.clear(); f_ntrk_.clear(); f_t21_.clear(); f_hasEle_.clear(); f_nset_.clear();
  f_x_.clear(); f_y_.clear(); f_z_.clear(); f_cxx_.clear(); f_cxy_.clear(); f_cyy_.clear(); f_czz_.clear(); f_chi2_.clear(); f_ptx_.clear(); f_pty_.clear(); f_ptz_.clear(); f_eW_.clear();

  // ---- truth
  edm::Handle<reco::GenParticleCollection> gps;
  if (!isData_ && iEvent.getByLabel("genParticles", gps) && gps.isValid()) {
    for (size_t i = 0; i < gps->size(); ++i) {
      const reco::GenParticle& g = (*gps)[i];
      if (std::abs(g.pdgId()) != lwPdg_) continue;
      bool isLast = true; for (size_t d = 0; d < g.numberOfDaughters(); ++d) if (g.daughter(d)->pdgId() == g.pdgId()) isLast = false;
      if (!isLast) continue;
      const reco::Candidate *ee = 0, *zz = 0;
      for (size_t d = 0; d < g.numberOfDaughters(); ++d) {
        int id = std::abs(g.daughter(d)->pdgId());
        if (id == 11) ee = g.daughter(d);
        if (id == 23) zz = g.daughter(d);
      }
      if (!ee) continue;
      const reco::Candidate* ef = lastCopy(ee);
      // production vertex of the first LW copy = true PV
      const reco::Candidate* first = &g;
      for (int it = 0; it < 100 && first->numberOfMothers() > 0 && first->mother(0)->pdgId() == g.pdgId(); ++it) first = first->mother(0);
      t_pvx_.push_back(first->vx()); t_pvy_.push_back(first->vy()); t_pvz_.push_back(first->vz());
      t_dvx_.push_back(ee->vx()); t_dvy_.push_back(ee->vy()); t_dvz_.push_back(ee->vz());
      t_lpt_.push_back(g.pt()); t_leta_.push_back(g.eta()); t_lphi_.push_back(g.phi()); t_lm_.push_back(g.mass());
      t_ept_.push_back(ef->pt()); t_eeta_.push_back(ef->eta()); t_ephi_.push_back(ef->phi()); t_eq_.push_back(ef->charge());
      std::vector<const reco::Candidate*> qs;
      if (zz) { const reco::Candidate* zl = lastCopy(zz); for (size_t d = 0; d < zl->numberOfDaughters(); ++d) if (std::abs(zl->daughter(d)->pdgId()) <= 5) qs.push_back(zl->daughter(d)); }
      t_q1pt_.push_back(qs.size() > 0 ? qs[0]->pt() : -1); t_q1eta_.push_back(qs.size() > 0 ? qs[0]->eta() : 0); t_q1phi_.push_back(qs.size() > 0 ? qs[0]->phi() : 0);
      t_q2pt_.push_back(qs.size() > 1 ? qs[1]->pt() : -1); t_q2eta_.push_back(qs.size() > 1 ? qs[1]->eta() : 0); t_q2phi_.push_back(qs.size() > 1 ? qs[1]->phi() : 0);
    }
  }
  // ---- reco objects + truth match
  for (int k = 0; k < 2; ++k) {
    int lw = -1;
    for (size_t t = 0; t < t_ept_.size(); ++t)
      if (t_eq_[t] == el[k]->charge() && reco::deltaR(t_eeta_[t], t_ephi_[t], el[k]->eta(), el[k]->phi()) < 0.1) lw = t;
    std::vector<double> drs;
    for (size_t i = 0; i < sj.size(); ++i) drs.push_back(reco::deltaR(el[k]->eta(), el[k]->phi(), sj[i].eta, sj[i].phi));
    std::sort(drs.begin(), drs.end());
    e_pt_.push_back(el[k]->pt()); e_eta_.push_back(el[k]->eta()); e_phi_.push_back(el[k]->phi()); e_q_.push_back(el[k]->charge());
    e_lw_.push_back(lw); e_dR1_.push_back(drs[0]); e_dR2_.push_back(drs[1]); e_drc_.push_back(std::fabs(drs[0] - drs[1]) < 0.2);
  }
  for (size_t i = 0; i < sj.size(); ++i) {
    int lw = -1; double best = 0.4;
    for (size_t t = 0; t < t_q1pt_.size(); ++t) {
      double d1 = t_q1pt_[t] > 0 ? reco::deltaR(t_q1eta_[t], t_q1phi_[t], sj[i].eta, sj[i].phi) : 9;
      double d2 = t_q2pt_[t] > 0 ? reco::deltaR(t_q2eta_[t], t_q2phi_[t], sj[i].eta, sj[i].phi) : 9;
      double d = std::min(d1, d2);
      if (d < best) { best = d; lw = 10 * t + (d1 < d2 ? 0 : 1); }   // 10*LW index + quark index
    }
    j_pt_.push_back(sj[i].pt); j_eta_.push_back(sj[i].eta); j_phi_.push_back(sj[i].phi); j_lw_.push_back(lw);
  }

  // ---- PV and vertex-track weights
  edm::Handle<reco::VertexCollection> pvs; iEvent.getByLabel("offlinePrimaryVertices", pvs);
  int ipv = -1; nPV_ = 0;
  for (size_t i = 0; i < pvs->size(); ++i) {
    const reco::Vertex& v = (*pvs)[i];
    if (v.isFake() || v.ndof() <= 4 || std::fabs(v.z()) > 24 || v.position().Rho() > 2) continue;
    ++nPV_; if (ipv < 0) ipv = i;
  }
  if (ipv < 0) ipv = 0;
  const reco::Vertex& pv = (*pvs)[ipv];
  pvx_ = pv.x(); pvy_ = pv.y(); pvz_ = pv.z(); pvcxx_ = pv.covariance(0,0); pvcxy_ = pv.covariance(0,1); pvcyy_ = pv.covariance(1,1);
  std::map<unsigned, float> wPV, wPU;
  for (size_t i = 0; i < pvs->size(); ++i) {
    const reco::Vertex& v = (*pvs)[i];
    if (v.isFake()) continue;
    for (reco::Vertex::trackRef_iterator it = v.tracks_begin(); it != v.tracks_end(); ++it) {
      float w = v.trackWeight(*it);
      unsigned key = it->key();
      std::map<unsigned, float>& m = (int(i) == ipv) ? wPV : wPU;
      if (w > m[key]) m[key] = w;
    }
  }
  edm::ESHandle<MagneticField> bfield; iSetup.get<IdealMagneticFieldRecord>().get(bfield);
  const MagneticField* mf = bfield.product();
  std::vector<std::vector<reco::TrackRef> > jtrk(sj.size());
  for (size_t i = 0; i < sj.size(); ++i) {
    std::vector<reco::PFCandidatePtr> cs = sj[i].jet->getPFConstituents();
    for (size_t c = 0; c < cs.size(); ++c) { reco::TrackRef tr = cs[c]->trackRef(); if (tr.isNonnull() && tr->pt() > 1.) jtrk[i].push_back(tr); }
  }
  // per-track cleaning decisions (key -> bitmask of cleaning settings that DROP it)
  std::map<unsigned, int> dropMask;
  for (size_t i = 0; i < sj.size(); ++i) for (size_t t = 0; t < jtrk[i].size(); ++t) {
    const reco::TrackRef& tr = jtrk[i][t];
    if (dropMask.count(tr.key())) continue;
    int m = 0;
    bool inPV = wPV.count(tr.key()) && wPV[tr.key()] > 0.5, inPU = wPU.count(tr.key()) && wPU[tr.key()] > 0.5;
    if (inPV || inPU) m |= 2;
    reco::TransientTrack tt(tr, mf);
    std::pair<bool, Measurement1D> ip = IPTools::absoluteTransverseImpactParameter(tt, pv);
    double sig = ip.first ? ip.second.significance() : 0;
    if (inPU || sig < 2) m |= 4;
    if (inPU || sig < 3) m |= 8;
    dropMask[tr.key()] = m;
  }

  for (int k = 0; k < 2; ++k) {
    reco::TransientTrack ett(ctf[k], mf);
    for (size_t a = 0; a < sj.size(); ++a) for (size_t b = a+1; b < sj.size(); ++b) {
      TLorentzVector ja(sj[a].px, sj[a].py, sj[a].pz, sj[a].e), jb(sj[b].px, sj[b].py, sj[b].pz, sj[b].e);
      double mjj = (ja + jb).M();
      if (mjj < 50 || mjj > 170) continue;
      TLorentzVector e4(el[k]->px(), el[k]->py(), el[k]->pz(), el[k]->energy());
      TLorentzVector tot = e4 + ja + jb;
      int ci = c_ele_.size();
      int truth = 0;
      int la = j_lw_[a], lb = j_lw_[b];
      if (la >= 0 && lb >= 0 && la / 10 == lb / 10 && la % 10 != lb % 10) truth = (e_lw_[k] >= 0 && la / 10 == e_lw_[k]) ? 1 : 2;
      c_ele_.push_back(k); c_j1_.push_back(a); c_j2_.push_back(b); c_truth_.push_back(truth);
      c_mjj_.push_back(mjj); c_mejj_.push_back(tot.M()); c_ptejj_.push_back(tot.Pt());
      c_px_.push_back(tot.Px()); c_py_.push_back(tot.Py()); c_pz_.push_back(tot.Pz());
      for (size_t icl = 0; icl < cleanings_.size(); ++icl) {
        int cl = cleanings_[icl];
        std::vector<reco::TransientTrack> tts; tts.push_back(ett);
        std::set<unsigned> keys; keys.insert(ctf[k].key());
        size_t jj[2] = {a, b};
        for (int q = 0; q < 2; ++q) for (size_t t = 0; t < jtrk[jj[q]].size(); ++t) {
          const reco::TrackRef& tr = jtrk[jj[q]][t];
          if (keys.count(tr.key())) continue;
          if (cl > 0 && (dropMask[tr.key()] & (1 << cl))) continue;
          keys.insert(tr.key()); tts.push_back(reco::TransientTrack(tr, mf));
        }
        int nset = tts.size();
        // fitter 0: SVRA, all SVs containing the electron
        bool doF[3] = {false, false, false};
        for (size_t q = 0; q < fitters_.size(); ++q) doF[fitters_[q]] = true;
        std::vector<FitV> vs; if (doF[0]) vs = svra(tts);
        std::sort(vs.begin(), vs.end(), [](const FitV& x, const FitV& y) { return x.trk.size() > y.trk.size() || (x.trk.size() == y.trk.size() && x.chi2ndf < y.chi2ndf); });
        int rank = 0;
        for (int fit = 0; fit < 3; ++fit) {
          if (!doF[fit]) continue;
          std::vector<FitV> rows;
          std::vector<std::vector<float> > wts;
          if (fit == 0) { for (size_t v = 0; v < vs.size(); ++v) if (vs[v].trk[0] == 0) { rows.push_back(vs[v]); wts.push_back(std::vector<float>(vs[v].trk.size(), 1.)); } }
          else if (nset >= 2) {
            std::vector<int> all; for (int t = 0; t < nset; ++t) all.push_back(t);
            if (fit == 1) { FitV f; int id = 0; if (fitKVF(tts, all, f, id, false)) { rows.push_back(f); wts.push_back(std::vector<float>(nset, 1.)); } }
            else {
              AdaptiveVertexFitter avf; TransientVertex tv;
              try { tv = avf.vertex(tts); } catch (...) {}
              if (tv.isValid() && tv.degreesOfFreedom() > 0) {
                FitV f; f.id = 0; f.v = reco::Vertex(tv); f.chi2ndf = tv.totalChiSquared() / tv.degreesOfFreedom();
                std::vector<float> w;
                for (int t = 0; t < nset; ++t) { float ww = tv.trackWeight(tts[t]); w.push_back(ww); if (ww > 0.5) f.trk.push_back(t); }
                rows.push_back(f); wts.push_back(w);
              }
            }
          }
          rank = 0;
          for (size_t r = 0; r < rows.size(); ++r) {
            const FitV& f = rows[r];
            int n3 = 0; bool pc = false, pw = false, al = true; double px = 0, py = 0, pz = 0;
            for (size_t t = 0; t < f.trk.size(); ++t) {
              const reco::Track& ta = tts[f.trk[t]].track();
              if (ta.p() > 3) ++n3; px += ta.px(); py += ta.py(); pz += ta.pz();
              for (size_t u = t+1; u < f.trk.size(); ++u) {
                const reco::Track& tb = tts[f.trk[u]].track();
                double dr = reco::deltaR(ta.eta(), ta.phi(), tb.eta(), tb.phi());
                if (dr < 0.4) pc = true; if (dr > 1.2) pw = true; if (!(dr < 4)) al = false;
              }
            }
            int t21 = 0;
            if (f.trk.size() >= 5) t21 |= 1; if (n3 >= 3) t21 |= 2; if (pc) t21 |= 4; if (pw) t21 |= 8; if (al) t21 |= 16;
            bool hasE = std::find(f.trk.begin(), f.trk.end(), 0) != f.trk.end();
            f_cand_.push_back(ci); f_clean_.push_back(cl); f_fitter_.push_back(fit); f_rank_.push_back(rank++);
            f_ntrk_.push_back(f.trk.size()); f_t21_.push_back(t21); f_hasEle_.push_back(hasE); f_nset_.push_back(nset);
            f_x_.push_back(f.v.x()); f_y_.push_back(f.v.y()); f_z_.push_back(f.v.z());
            f_cxx_.push_back(f.v.covariance(0,0)); f_cxy_.push_back(f.v.covariance(0,1)); f_cyy_.push_back(f.v.covariance(1,1)); f_czz_.push_back(f.v.covariance(2,2));
            f_chi2_.push_back(f.chi2ndf); f_ptx_.push_back(px); f_pty_.push_back(py); f_ptz_.push_back(pz);
            f_eW_.push_back(wts[r].empty() ? 0 : wts[r][0]);
          }
        }
      }
    }
  }
  tree_->Fill();
}

DEFINE_FWK_MODULE(WDVv3Analyzer);
