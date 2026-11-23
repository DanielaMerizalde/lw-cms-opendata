// WDVQCDAnalyzer = WDVAnalyzer v2 + electron ID/isolation variables for the data-driven QCD estimate.
// The event selection, SV reconstruction and kappa are IDENTICAL to v2 (no ID or isolation cut is applied);
// additions (2026-11-09):
//   * per-electron ID variables and flags (2012 cut-based EGamma ID, copied from POET ElectronAnalyzer.cc,
//     branch 2012): e_iso (PF relative iso, rho*Aeff corrected), e_idBits (loose/medium/tight with and
//     without the isolation requirement), and the raw ID variables, in the "events" tree;
//   * a second tree "elA" ("level A"): every event passing trigger + TO + HQ, with or without jets
//     (TF and JetS are NOT required there), with the same electron variables, m_ee, and jet counts.
//     It is used to measure R = OS/SS in the anti-isolated region and the tight-to-loose fake factor.
// The cutflow histograms count exactly as in v2.
//
// ---- original v2 header ----
// WDVAnalyzer v2: reproduction of J. Sanchez, ACI 15(1) 2780 (2023) and of the author's MSc thesis
// (USFQ 2022, Chapter II): selection NF/TF/TO/HQ/JetS/DRC/SG/IPP, secondary-vertex reconstruction
// (SVRA) on electron + jet-pair track sets, and the transverse parallelity
//   kappa_par = (PV->SV)_T . P_T   [mm GeV].
// CMSSW_5_3_32.  Lee-Wick reproduction project, phase 3B.
//
// Output: TTree "events" (events passing DRC, any charge combination), lumi-section tree,
// cutflow histograms for the opposite-sign (OS) and same-sign (SS, QCD control) chains.

#include <memory>
#include <vector>
#include <string>
#include <set>
#include <map>
#include <algorithm>
#include <cmath>
#include <fstream>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "DataFormats/HLTReco/interface/TriggerObject.h"
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"
#include "DataFormats/EgammaCandidates/interface/ConversionFwd.h"
#include "RecoEgamma/EgammaTools/interface/ConversionTools.h"
#include "DataFormats/GsfTrackReco/interface/GsfTrack.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "JetMETCorrections/Objects/interface/JetCorrector.h"

#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"

#include "TTree.h"
#include "TH1D.h"
#include "TLorentzVector.h"

namespace {
  struct SelJet { const reco::PFJet* jet; double pt, eta, phi, e, px, py, pz, emf; int nconst; bool good; };
  struct FitV { int id; std::vector<int> trk; reco::Vertex v; double chi2ndf; };
  bool byPt(const SelJet& a, const SelJet& b) { return a.pt > b.pt; }

  // 2012 cut-based electron ID exactly as in POET (PhysObjectExtractorTool, branch 2012, ElectronAnalyzer.cc).
  // idBits: 1 loose, 2 medium, 4 tight (with isolation, = POET isLoose/isMedium/isTight);
  //         8 loose, 16 medium, 32 tight WITHOUT the isolation requirement (for the anti-isolated region).
  struct EleID { float iso, sieie, hoe, deta, dphi, dxy, dz, ooemoop; int mhits, convVeto, idBits; };

  float effArea03(float eta) {   // POET effectiveArea0p3cone
    eta = std::fabs(eta);
    if (eta < 1.0) return 0.13;  if (eta < 1.479) return 0.14; if (eta < 2.0) return 0.07;
    if (eta < 2.2) return 0.09;  if (eta < 2.3) return 0.11;   if (eta < 2.4) return 0.11;
    return 0.14;
  }

  EleID computeID(const reco::GsfElectron& e, const math::XYZPoint& pv, const edm::Handle<reco::ConversionCollection>& conv,
                  const math::XYZPoint& bs, double rho) {
    EleID r;
    reco::GsfTrackRef trk = e.gsfTrack();
    // POET computes trackerExpectedHitsInner().numberOfHits() - hitPattern().numberOfHits(), which is always
    // negative (inner missing hits minus ALL valid hits), so its "missing hits" cut never acts. We use the
    // standard 2012 EGamma definition: number of missing inner hits.
    r.mhits = trk->trackerExpectedHitsInner().numberOfHits();
    r.convVeto = conv.isValid() ? !ConversionTools::hasMatchedConversion(e, conv, bs) : -1;
    r.iso = 999;
    if (e.passingPflowPreselection()) {
      const reco::GsfElectron::PflowIsolationVariables& pf = e.pfIsolationVariables();
      r.iso = (pf.chargedHadronIso + std::max(0.0, pf.neutralHadronIso + pf.photonIso - rho * effArea03(e.eta()))) / e.pt();
    }
    r.sieie = e.sigmaIetaIeta(); r.hoe = e.hadronicOverEm();
    r.deta = std::fabs(e.deltaEtaSuperClusterTrackAtVtx()); r.dphi = std::fabs(e.deltaPhiSuperClusterTrackAtVtx());
    r.dxy = trk->dxy(pv); r.dz = trk->dz(pv);
    r.ooemoop = std::fabs(1. / e.ecalEnergy() - 1. / (e.ecalEnergy() / e.eSuperClusterOverP()));
    double adxy = std::fabs(r.dxy), adz = std::fabs(r.dz);
    bool cv = (r.convVeto == 1);
    bool L = false, M = false, T = false;   // without isolation
    bool isoL = r.iso < .15, isoT = r.iso < .10;
    if (std::fabs(e.eta()) <= 1.479) {
      L = r.deta < .007 && r.dphi < .15 && r.sieie < .01 && r.hoe < .12 && adxy < .02 && adz < .2 &&
          r.mhits <= 1 && cv && r.ooemoop < .05;
      M = L && r.deta < .004 && r.dphi < .06 && adz < .1;
      T = M && r.dphi < .03 && r.mhits <= 0;
    } else if (std::fabs(e.eta()) < 2.5) {
      L = r.deta < .009 && r.dphi < .1 && r.sieie < .03 && r.hoe < .1 && adxy < .02 && adz < .2 &&
          r.mhits <= 1 && cv && r.ooemoop < .05;
      M = L && r.deta < .007 && r.dphi < .03 && adz < .1;
      T = M && r.deta < .005 && r.dphi < .02 && r.mhits <= 0;
    }
    r.idBits = (L && isoL ? 1 : 0) | (M && isoL ? 2 : 0) | (T && isoL && isoT ? 4 : 0) |
               (L ? 8 : 0) | (M ? 16 : 0) | (T ? 32 : 0);
    return r;
  }
}

class WDVQCDAnalyzer : public edm::EDAnalyzer {
public:
  explicit WDVQCDAnalyzer(const edm::ParameterSet&);
  ~WDVQCDAnalyzer() {}
private:
  virtual void beginJob();
  virtual void beginRun(const edm::Run&, const edm::EventSetup&);
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  virtual void endLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&);

  bool fitTracks(const std::vector<reco::TransientTrack>& tts, const std::vector<int>& idx, FitV& out, int& nextId) const;
  std::vector<FitV> svra(const std::vector<reco::TransientTrack>& tts) const;
  void fillCut(int bin, bool os, bool ss);

  bool isData_;
  std::vector<std::string> hltThesis_, hltExtra_;
  std::string jecName_;
  double tfEleEt_, tfJetPt_; int tfNJets_;
  double eleLeadPt_, eleSubPt_, eleEta_, trigMatchDR_;
  double jetPt_, jetEta_, jetNHEF_, jetNEMEF_, jetMEF_, jetEMF_; int jetMinConst_, nJetsMin_;
  double dRdiff_, mjjLo_, mjjHi_;
  double trkPt_; int trkMinHits_, trkMinPix_;
  double chi2Max_; int svMinTrk_, svMinTrk3_; double svTrkE_, mergeSig_;
  double dRclose_, dRwide_, dRmax_;
  int dRmaxMode_;   // Table 2.1 row 5: 0 = all track pairs dR < dRmax, 1 = some pair dR > dRmax (literal reading)
  double ippLT_, ippPT_;
  int lwPdg_; double genMatchDR_;
  // two-pass mode: levelAOnly = stop before the SV step (no generalTracks/particleFlow needed) and list the
  // events that reach it in selList (one "run:event" per line) for the second pass
  bool levelAOnly_; std::string selListName_; std::ofstream selList_;
  // lazyHQ: single pass; HQ (needs generalTracks) is evaluated only for events that reach the SV step, so
  // the heavy collections are read only for those few events (level-A rows get hq = -1)
  bool lazyHQ_;
  bool useTrigMatch_;

  HLTConfigProvider hltConfig_;
  bool hltOk_;

  TTree *tree_, *lumiTree_;
  TH1D *hCutOS_, *hCutSS_, *hCutOSw_, *hCutSSw_;
  double curW_;

  unsigned int run_, lumi_; unsigned long long evt_;
  float genW_, nTrueInt_; int nPV_, hltBits_, toMatched_;
  float pvx_, pvy_, pvz_;
  int isOS_, isSS_, passDRC_, passIPP_, passIPPflip_, nSigEle_;
  int lrun_, llumi_;
  std::vector<float> e_pt_, e_eta_, e_phi_, e_dR1_, e_dR2_;
  std::vector<int> e_q_, e_hp_, e_drc_, e_sig_, e_ipp_, e_ippflip_;
  std::vector<float> j_pt_, j_eta_, j_phi_, j_emf_;
  std::vector<float> sv_x_, sv_y_, sv_z_, sv_chi2ndf_, sv_LT_, sv_L3D_, sv_LTsig_;
  std::vector<float> sv_k_, sv_kobjT_, sv_k3trk_, sv_k3obj_, sv_ptT_, sv_ptTobj_, sv_mjj_, sv_mejj_;
  std::vector<int> sv_ntrk_, sv_ele_, sv_j1_, sv_j2_, sv_flags_, sv_hasEle_, sv_sig_;
  std::vector<float> g_pt_, g_eta_, g_phi_, g_vx_, g_vy_, g_vz_;
  std::vector<int> g_id_, g_mid_;
  // electron ID (filled for the two selected electrons, same order as e_*; shared by both trees)
  std::vector<float> e_iso_, e_sieie_, e_hoe_, e_deta_, e_dphi_, e_dxy_, e_dz_, e_ooemoop_;
  std::vector<int> e_mhits_, e_convVeto_, e_idBits_;
  // level-A tree (trigger + TO + HQ, no jet requirement)
  TTree* treeA_;
  std::vector<float> a_pt_, a_eta_, a_phi_;
  std::vector<int> a_q_;
  float a_mee_, a_rho_;
  int a_isOS_, a_passTF_, a_nJetTF_, a_nJetGood_;
  int a_hq_;   // 1 = HQ applied, -1 = not evaluated (pass 1 of the two-pass mode)
};

WDVQCDAnalyzer::WDVQCDAnalyzer(const edm::ParameterSet& p) :
  isData_(p.getParameter<bool>("isData")),
  hltThesis_(p.getParameter<std::vector<std::string> >("hltThesis")),
  hltExtra_(p.getParameter<std::vector<std::string> >("hltExtra")),
  jecName_(p.getParameter<std::string>("jecName")),
  tfEleEt_(p.getParameter<double>("tfElePt")), tfJetPt_(p.getParameter<double>("tfJetPt")),
  tfNJets_(p.getParameter<int>("tfNJets")),
  eleLeadPt_(p.getParameter<double>("eleLeadPt")), eleSubPt_(p.getParameter<double>("eleSubPt")),
  eleEta_(p.getParameter<double>("eleEta")), trigMatchDR_(p.getParameter<double>("trigMatchDR")),
  jetPt_(p.getParameter<double>("jetPt")), jetEta_(p.getParameter<double>("jetEta")),
  jetNHEF_(p.getParameter<double>("jetNHEF")), jetNEMEF_(p.getParameter<double>("jetNEMEF")),
  jetMEF_(p.getParameter<double>("jetMEF")), jetEMF_(p.getParameter<double>("jetEMF")),
  jetMinConst_(p.getParameter<int>("jetMinConst")), nJetsMin_(p.getParameter<int>("nJetsMin")),
  dRdiff_(p.getParameter<double>("dRdiff")),
  mjjLo_(p.getParameter<double>("mjjLo")), mjjHi_(p.getParameter<double>("mjjHi")),
  trkPt_(p.getParameter<double>("trkPt")), trkMinHits_(p.getParameter<int>("trkMinHits")),
  trkMinPix_(p.getParameter<int>("trkMinPix")),
  chi2Max_(p.getParameter<double>("chi2Max")), svMinTrk_(p.getParameter<int>("svMinTrk")),
  svMinTrk3_(p.getParameter<int>("svMinTrk3")), svTrkE_(p.getParameter<double>("svTrkE")),
  mergeSig_(p.getParameter<double>("mergeSig")),
  dRclose_(p.getParameter<double>("dRclose")), dRwide_(p.getParameter<double>("dRwide")),
  dRmax_(p.getParameter<double>("dRmax")),
  dRmaxMode_(p.getParameter<int>("dRmaxMode")),
  ippLT_(p.getParameter<double>("ippLT")), ippPT_(p.getParameter<double>("ippPT")),
  lwPdg_(p.getParameter<int>("lwPdg")), genMatchDR_(p.getParameter<double>("genMatchDR")),
  levelAOnly_(p.getUntrackedParameter<bool>("levelAOnly", false)),
  selListName_(p.getUntrackedParameter<std::string>("selList", "")),
  lazyHQ_(p.getUntrackedParameter<bool>("lazyHQ", false)),
  useTrigMatch_(p.getParameter<bool>("useTrigMatch")),
  hltOk_(false), curW_(1.)
{}

void WDVQCDAnalyzer::beginRun(const edm::Run& r, const edm::EventSetup& es) {
  bool changed = false;
  hltOk_ = hltConfig_.init(r, es, "HLT", changed);
}

void WDVQCDAnalyzer::beginJob() {
  edm::Service<TFileService> fs;
  if (!selListName_.empty()) selList_.open(selListName_.c_str());
  const char* labels[8] = {"NF", "TF", "TO", "HQ", "JetS", "DRC", "SG", "IPP"};
  hCutOS_  = fs->make<TH1D>("cutflow_os",  "cutflow OS chain (events);;events", 8, 0, 8);
  hCutSS_  = fs->make<TH1D>("cutflow_ss",  "cutflow SS chain (events);;events", 8, 0, 8);
  hCutOSw_ = fs->make<TH1D>("cutflow_os_w","cutflow OS chain (sum gen-weight signs);;", 8, 0, 8);
  hCutSSw_ = fs->make<TH1D>("cutflow_ss_w","cutflow SS chain (sum gen-weight signs);;", 8, 0, 8);
  for (int i = 0; i < 8; ++i) {
    hCutOS_->GetXaxis()->SetBinLabel(i+1, labels[i]); hCutSS_->GetXaxis()->SetBinLabel(i+1, labels[i]);
    hCutOSw_->GetXaxis()->SetBinLabel(i+1, labels[i]); hCutSSw_->GetXaxis()->SetBinLabel(i+1, labels[i]);
  }
  lumiTree_ = fs->make<TTree>("lumis", "processed lumi sections");
  lumiTree_->Branch("run", &lrun_, "run/I");
  lumiTree_->Branch("lumi", &llumi_, "lumi/I");

  tree_ = fs->make<TTree>("events", "WDV analysis (events passing DRC)");
  tree_->Branch("run", &run_, "run/i"); tree_->Branch("lumi", &lumi_, "lumi/i"); tree_->Branch("event", &evt_, "event/l");
  tree_->Branch("genW", &genW_, "genW/F"); tree_->Branch("nTrueInt", &nTrueInt_, "nTrueInt/F");
  tree_->Branch("nPV", &nPV_, "nPV/I"); tree_->Branch("hltBits", &hltBits_, "hltBits/I");
  tree_->Branch("toMatched", &toMatched_, "toMatched/I");
  tree_->Branch("pvx", &pvx_, "pvx/F"); tree_->Branch("pvy", &pvy_, "pvy/F"); tree_->Branch("pvz", &pvz_, "pvz/F");
  tree_->Branch("isOS", &isOS_, "isOS/I"); tree_->Branch("isSS", &isSS_, "isSS/I");
  tree_->Branch("passDRC", &passDRC_, "passDRC/I");
  tree_->Branch("passIPP", &passIPP_, "passIPP/I"); tree_->Branch("passIPPflip", &passIPPflip_, "passIPPflip/I");
  tree_->Branch("nSigEle", &nSigEle_, "nSigEle/I");
  tree_->Branch("e_pt", &e_pt_); tree_->Branch("e_eta", &e_eta_); tree_->Branch("e_phi", &e_phi_);
  tree_->Branch("e_q", &e_q_); tree_->Branch("e_hp", &e_hp_); tree_->Branch("e_dR1", &e_dR1_); tree_->Branch("e_dR2", &e_dR2_);
  tree_->Branch("e_drc", &e_drc_); tree_->Branch("e_sig", &e_sig_); tree_->Branch("e_ipp", &e_ipp_); tree_->Branch("e_ippflip", &e_ippflip_);
  tree_->Branch("j_pt", &j_pt_); tree_->Branch("j_eta", &j_eta_); tree_->Branch("j_phi", &j_phi_); tree_->Branch("j_emf", &j_emf_);
  tree_->Branch("sv_x", &sv_x_); tree_->Branch("sv_y", &sv_y_); tree_->Branch("sv_z", &sv_z_);
  tree_->Branch("sv_ntrk", &sv_ntrk_); tree_->Branch("sv_chi2ndf", &sv_chi2ndf_);
  tree_->Branch("sv_LT", &sv_LT_); tree_->Branch("sv_LTsig", &sv_LTsig_); tree_->Branch("sv_L3D", &sv_L3D_);
  tree_->Branch("sv_k", &sv_k_); tree_->Branch("sv_kobjT", &sv_kobjT_);
  tree_->Branch("sv_k3trk", &sv_k3trk_); tree_->Branch("sv_k3obj", &sv_k3obj_);
  tree_->Branch("sv_ptT", &sv_ptT_); tree_->Branch("sv_ptTobj", &sv_ptTobj_);
  tree_->Branch("sv_mjj", &sv_mjj_); tree_->Branch("sv_mejj", &sv_mejj_);
  tree_->Branch("sv_ele", &sv_ele_); tree_->Branch("sv_j1", &sv_j1_); tree_->Branch("sv_j2", &sv_j2_);
  tree_->Branch("sv_flags", &sv_flags_); tree_->Branch("sv_hasEle", &sv_hasEle_); tree_->Branch("sv_sig", &sv_sig_);
  tree_->Branch("g_pt", &g_pt_); tree_->Branch("g_eta", &g_eta_); tree_->Branch("g_phi", &g_phi_);
  tree_->Branch("g_vx", &g_vx_); tree_->Branch("g_vy", &g_vy_); tree_->Branch("g_vz", &g_vz_);
  tree_->Branch("g_id", &g_id_); tree_->Branch("g_mid", &g_mid_);

  // electron ID branches (both trees point to the same vectors)
  treeA_ = fs->make<TTree>("elA", "level A: trigger + TO + HQ, no jet requirement (QCD control)");
  treeA_->Branch("run", &run_, "run/i"); treeA_->Branch("lumi", &lumi_, "lumi/i"); treeA_->Branch("event", &evt_, "event/l");
  treeA_->Branch("genW", &genW_, "genW/F"); treeA_->Branch("nPV", &nPV_, "nPV/I");
  treeA_->Branch("hltBits", &hltBits_, "hltBits/I"); treeA_->Branch("toMatched", &toMatched_, "toMatched/I");
  treeA_->Branch("isOS", &a_isOS_, "isOS/I"); treeA_->Branch("mee", &a_mee_, "mee/F"); treeA_->Branch("rho", &a_rho_, "rho/F");
  treeA_->Branch("passTF", &a_passTF_, "passTF/I"); treeA_->Branch("hq", &a_hq_, "hq/I");
  treeA_->Branch("nJetTF", &a_nJetTF_, "nJetTF/I"); treeA_->Branch("nJetGood", &a_nJetGood_, "nJetGood/I");
  treeA_->Branch("e_pt", &a_pt_); treeA_->Branch("e_eta", &a_eta_); treeA_->Branch("e_phi", &a_phi_); treeA_->Branch("e_q", &a_q_);
  TTree* tt[2] = {tree_, treeA_};
  for (int t = 0; t < 2; ++t) {
    tt[t]->Branch("e_iso", &e_iso_); tt[t]->Branch("e_idBits", &e_idBits_);
    tt[t]->Branch("e_sieie", &e_sieie_); tt[t]->Branch("e_hoe", &e_hoe_);
    tt[t]->Branch("e_deta", &e_deta_); tt[t]->Branch("e_dphi", &e_dphi_);
    tt[t]->Branch("e_dxy", &e_dxy_); tt[t]->Branch("e_dz", &e_dz_); tt[t]->Branch("e_ooemoop", &e_ooemoop_);
    tt[t]->Branch("e_mhits", &e_mhits_); tt[t]->Branch("e_convVeto", &e_convVeto_);
  }
}

void WDVQCDAnalyzer::endLuminosityBlock(const edm::LuminosityBlock& lb, const edm::EventSetup&) {
  lrun_ = lb.run(); llumi_ = lb.luminosityBlock(); lumiTree_->Fill();
}

void WDVQCDAnalyzer::fillCut(int bin, bool os, bool ss) {
  if (os) { hCutOS_->Fill(bin); hCutOSw_->Fill(bin, curW_); }
  if (ss) { hCutSS_->Fill(bin); hCutSSw_->Fill(bin, curW_); }
}

bool WDVQCDAnalyzer::fitTracks(const std::vector<reco::TransientTrack>& tts, const std::vector<int>& idx, FitV& out, int& nextId) const {
  if (idx.size() < 2) return false;
  std::vector<reco::TransientTrack> v; v.reserve(idx.size());
  for (size_t i = 0; i < idx.size(); ++i) v.push_back(tts[idx[i]]);
  KalmanVertexFitter kvf(false);
  TransientVertex tv;
  try { tv = kvf.vertex(v); } catch (...) { return false; }
  if (!tv.isValid() || tv.degreesOfFreedom() <= 0) return false;
  double c = tv.totalChiSquared() / tv.degreesOfFreedom();
  if (!(c < chi2Max_)) return false;
  out.trk = idx; std::sort(out.trk.begin(), out.trk.end());
  out.v = reco::Vertex(tv); out.chi2ndf = c; out.id = nextId++;
  return true;
}

// SVRA as described in the thesis (Sec. 2.1.4): all track pairs fitted with KVF (chi2/ndf<5);
// two vertices sharing tracks are refitted together; the merged vertex replaces both if
// chi2/ndf<5 and it is geometrically compatible (3D distance significance between the two
// vertices < mergeSig, as in arXiv:1610.05133); otherwise both are kept (the pair is not retried).
// Iterate until no untried pair of vertices shares tracks.
std::vector<FitV> WDVQCDAnalyzer::svra(const std::vector<reco::TransientTrack>& tts) const {
  std::vector<FitV> vs;
  int nextId = 0;
  int n = tts.size();
  for (int i = 0; i < n; ++i) for (int j = i+1; j < n; ++j) {
    std::vector<int> idx(2); idx[0] = i; idx[1] = j;
    FitV f; if (fitTracks(tts, idx, f, nextId)) vs.push_back(f);
  }
  VertexDistance3D vd;
  std::set<std::pair<int,int> > tried;
  bool again = true;
  int guard = 0;
  while (again && guard++ < 20000) {
    again = false;
    for (size_t a = 0; a < vs.size() && !again; ++a) for (size_t b = a+1; b < vs.size(); ++b) {
      std::pair<int,int> key(std::min(vs[a].id, vs[b].id), std::max(vs[a].id, vs[b].id));
      if (tried.count(key)) continue;
      std::vector<int> shared;
      std::set_intersection(vs[a].trk.begin(), vs[a].trk.end(), vs[b].trk.begin(), vs[b].trk.end(), std::back_inserter(shared));
      if (shared.empty()) continue;
      tried.insert(key);
      double sig = vd.distance(vs[a].v, vs[b].v).significance();
      if (!(sig < mergeSig_)) continue;
      std::vector<int> uni;
      std::set_union(vs[a].trk.begin(), vs[a].trk.end(), vs[b].trk.begin(), vs[b].trk.end(), std::back_inserter(uni));
      FitV m;
      if (!fitTracks(tts, uni, m, nextId)) continue;
      vs.erase(vs.begin() + b); vs.erase(vs.begin() + a);
      vs.push_back(m);
      again = true;
      break;
    }
  }
  std::vector<FitV> out;
  for (size_t a = 0; a < vs.size(); ++a) {
    bool dup = false;
    for (size_t b = 0; b < out.size(); ++b) if (out[b].trk == vs[a].trk) { dup = true; break; }
    if (!dup) out.push_back(vs[a]);
  }
  return out;
}

void WDVQCDAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  curW_ = 1.; genW_ = 1.; nTrueInt_ = -1;
  if (!isData_) {
    edm::Handle<GenEventInfoProduct> gi;
    if (iEvent.getByLabel("generator", gi) && gi.isValid()) curW_ = gi->weight() >= 0 ? 1. : -1.;
    genW_ = curW_;
  }
  fillCut(0, true, true);   // NF

  // ---------------- TF: thesis trigger OR + >=2 GSF electrons pT>20 + >=4 jets pT>15
  edm::Handle<edm::TriggerResults> trh;
  iEvent.getByLabel(edm::InputTag("TriggerResults", "", "HLT"), trh);
  hltBits_ = 0;
  std::vector<std::string> firedPaths;
  if (trh.isValid()) {
    const edm::TriggerNames& tn = iEvent.triggerNames(*trh);
    for (unsigned i = 0; i < tn.size(); ++i) {
      if (!trh->accept(i)) continue;
      const std::string& nm = tn.triggerName(i);
      for (size_t k = 0; k < hltThesis_.size(); ++k)
        if (nm.compare(0, hltThesis_[k].size(), hltThesis_[k]) == 0) { hltBits_ |= (1 << k); firedPaths.push_back(nm); }
      for (size_t k = 0; k < hltExtra_.size(); ++k)
        if (nm.compare(0, hltExtra_[k].size(), hltExtra_[k]) == 0) hltBits_ |= (1 << (8 + k));
    }
  }
  if ((hltBits_ & 0xff) == 0) return;

  edm::Handle<reco::GsfElectronCollection> eles;
  iEvent.getByLabel("gsfElectrons", eles);
  int nE20 = 0;
  for (size_t i = 0; i < eles->size(); ++i) if ((*eles)[i].pt() > tfEleEt_) ++nE20;
  if (nE20 < 2) return;

  edm::Handle<reco::PFJetCollection> jets;
  iEvent.getByLabel("ak5PFJets", jets);
  const JetCorrector* corr = JetCorrector::getJetCorrector(jecName_, iSetup);
  std::vector<SelJet> alljets;
  int nTF = 0;
  for (size_t i = 0; i < jets->size(); ++i) {
    const reco::PFJet& j = (*jets)[i];
    double s = corr->correction(j, iEvent, iSetup);
    SelJet sj; sj.jet = &j; sj.pt = j.pt()*s; sj.eta = j.eta(); sj.phi = j.phi(); sj.e = j.energy()*s;
    sj.px = j.px()*s; sj.py = j.py()*s; sj.pz = j.pz()*s;
    sj.emf = j.chargedEmEnergyFraction() + j.neutralEmEnergyFraction();
    sj.nconst = j.nConstituents();
    sj.good = sj.pt > jetPt_ && std::fabs(sj.eta) < jetEta_ && sj.nconst > jetMinConst_ - 1 &&
              j.neutralHadronEnergyFraction() < jetNHEF_ && j.neutralEmEnergyFraction() < jetNEMEF_ &&
              j.muonEnergyFraction() < jetMEF_ && sj.emf < jetEMF_;
    if (sj.pt > tfJetPt_) ++nTF;
    alljets.push_back(sj);
  }
  // v2 returned here when TF failed; now the event continues to TO+HQ to fill the level-A tree, and the
  // cutflow bins (TF, TO, HQ) are only filled when TF passes, so the cutflow is identical to v2.
  const bool passTF = (nTF >= tfNJets_);
  if (passTF) fillCut(1, true, true);   // TF

  // ---------------- TO: the two leading trigger egamma objects reconstructed as GSF electrons, pT>40/25
  std::vector<int> toIdx;   // indices into eles
  toMatched_ = 0;
  if (useTrigMatch_ && hltOk_) {
    edm::Handle<trigger::TriggerEvent> tev;
    iEvent.getByLabel(edm::InputTag("hltTriggerSummaryAOD", "", "HLT"), tev);
    if (tev.isValid()) {
      std::set<trigger::size_type> keys;
      for (size_t p = 0; p < firedPaths.size(); ++p) {
        if (hltConfig_.triggerIndex(firedPaths[p]) >= hltConfig_.size()) continue;
        const std::vector<std::string>& mods = hltConfig_.moduleLabels(firedPaths[p]);
        // last filter of the path with saved objects (final egamma objects of the path)
        for (int m = int(mods.size()) - 1; m >= 0; --m) {
          trigger::size_type fi = tev->filterIndex(edm::InputTag(mods[m], "", "HLT"));
          if (fi >= tev->sizeFilters()) continue;
          const trigger::Keys& ks = tev->filterKeys(fi);
          for (size_t k = 0; k < ks.size(); ++k) keys.insert(ks[k]);
          break;
        }
      }
      const trigger::TriggerObjectCollection& objs = tev->getObjects();
      std::vector<std::pair<double, trigger::size_type> > cand;
      for (std::set<trigger::size_type>::const_iterator k = keys.begin(); k != keys.end(); ++k) {
        int id = std::abs(objs[*k].id());
        if (id != 81 && id != 82 && id != 92 && id != 0 && id != 22 && id != 11) continue;  // egamma-type objects
        cand.push_back(std::make_pair(objs[*k].pt(), *k));
      }
      std::sort(cand.rbegin(), cand.rend());
      std::vector<trigger::size_type> lead;
      for (size_t c = 0; c < cand.size() && lead.size() < 2; ++c) {
        bool dup = false;
        for (size_t l = 0; l < lead.size(); ++l)
          if (reco::deltaR(objs[lead[l]].eta(), objs[lead[l]].phi(), objs[cand[c].second].eta(), objs[cand[c].second].phi()) < 0.1) dup = true;
        if (!dup) lead.push_back(cand[c].second);
      }
      for (size_t l = 0; l < lead.size(); ++l) {
        int best = -1; double bdr = trigMatchDR_;
        for (size_t i = 0; i < eles->size(); ++i) {
          double dr = reco::deltaR(objs[lead[l]].eta(), objs[lead[l]].phi(), (*eles)[i].superCluster()->eta(), (*eles)[i].superCluster()->phi());
          if (dr < bdr && std::find(toIdx.begin(), toIdx.end(), (int)i) == toIdx.end()) { bdr = dr; best = i; }
        }
        if (best >= 0) toIdx.push_back(best);
      }
      toMatched_ = toIdx.size();
    }
  }
  if (!useTrigMatch_ || !hltOk_) {   // fallback: two highest-pT GSF electrons
    std::vector<std::pair<double,int> > ep;
    for (size_t i = 0; i < eles->size(); ++i) ep.push_back(std::make_pair((*eles)[i].pt(), (int)i));
    std::sort(ep.rbegin(), ep.rend());
    for (size_t i = 0; i < ep.size() && i < 2; ++i) toIdx.push_back(ep[i].second);
    toMatched_ = -1;
  }
  if (toIdx.size() < 2) return;
  const reco::GsfElectron* el[2] = {&(*eles)[toIdx[0]], &(*eles)[toIdx[1]]};
  if (el[1]->pt() > el[0]->pt()) std::swap(el[0], el[1]);
  if (el[0]->pt() < eleLeadPt_ || el[1]->pt() < eleSubPt_) return;
  if (std::fabs(el[0]->superCluster()->eta()) > eleEta_ || std::fabs(el[1]->superCluster()->eta()) > eleEta_) return;
  bool os = el[0]->charge() * el[1]->charge() < 0, ss = !os;
  if (passTF) fillCut(2, true, true);   // TO (charge not yet required)

  // ---------------- HQ: both electrons with a high-purity track (JHEP 02 (2013) 085)
  reco::TrackRef ctf[2];
  bool hp[2];
  // pass 1 (levelAOnly): generalTracks is not read, so HQ is not evaluated here (a_hq_ = -1); it is applied
  // in pass 2, which runs this full analyzer on the events listed in selList.
  if (levelAOnly_ || lazyHQ_) { hp[0] = hp[1] = true; a_hq_ = -1; }
  else {
  for (int k = 0; k < 2; ++k) {
    ctf[k] = el[k]->closestCtfTrackRef();
    hp[k] = ctf[k].isNonnull() && ctf[k]->quality(reco::TrackBase::highPurity);
  }
  a_hq_ = 1;
  }
  if (!(hp[0] && hp[1])) return;
  if (passTF) fillCut(3, true, true);

  // ---------------- PV (moved up from v2: needed for the electron dxy/dz; same choice as v2)
  edm::Handle<reco::VertexCollection> pvs;
  iEvent.getByLabel("offlinePrimaryVertices", pvs);
  const reco::Vertex* pv = 0; nPV_ = 0;
  for (size_t i = 0; i < pvs->size(); ++i) {
    const reco::Vertex& v = (*pvs)[i];
    if (v.isFake() || v.ndof() <= 4 || std::fabs(v.z()) > 24 || v.position().Rho() > 2) continue;
    ++nPV_; if (!pv) pv = &v;   // sorted by sum pT^2
  }
  if (!pv) pv = &(*pvs)[0];
  pvx_ = pv->x(); pvy_ = pv->y(); pvz_ = pv->z();
  run_ = iEvent.id().run(); lumi_ = iEvent.luminosityBlock(); evt_ = iEvent.id().event();

  // ---------------- electron ID (POET 2012 cut-based) for the two selected electrons
  edm::Handle<reco::ConversionCollection> hConv;
  iEvent.getByLabel("allConversions", hConv);
  edm::Handle<reco::BeamSpot> hBS;
  iEvent.getByLabel("offlineBeamSpot", hBS);
  edm::Handle<double> hRho;
  iEvent.getByLabel(edm::InputTag("fixedGridRhoAll"), hRho);
  const double rho = hRho.isValid() ? *hRho : 0.;
  const math::XYZPoint bsPos = hBS.isValid() ? hBS->position() : math::XYZPoint(0, 0, 0);
  e_iso_.clear(); e_sieie_.clear(); e_hoe_.clear(); e_deta_.clear(); e_dphi_.clear(); e_dxy_.clear(); e_dz_.clear();
  e_ooemoop_.clear(); e_mhits_.clear(); e_convVeto_.clear(); e_idBits_.clear();
  a_pt_.clear(); a_eta_.clear(); a_phi_.clear(); a_q_.clear();
  for (int k = 0; k < 2; ++k) {
    EleID id = computeID(*el[k], pv->position(), hConv, bsPos, rho);
    e_iso_.push_back(id.iso); e_sieie_.push_back(id.sieie); e_hoe_.push_back(id.hoe);
    e_deta_.push_back(id.deta); e_dphi_.push_back(id.dphi); e_dxy_.push_back(id.dxy); e_dz_.push_back(id.dz);
    e_ooemoop_.push_back(id.ooemoop); e_mhits_.push_back(id.mhits); e_convVeto_.push_back(id.convVeto);
    e_idBits_.push_back(id.idBits);
    a_pt_.push_back(el[k]->pt()); a_eta_.push_back(el[k]->eta()); a_phi_.push_back(el[k]->phi()); a_q_.push_back(el[k]->charge());
  }

  // ---------------- level-A tree: all events at this point (no jet requirement)
  {
    TLorentzVector p0(el[0]->px(), el[0]->py(), el[0]->pz(), el[0]->energy());
    TLorentzVector p1(el[1]->px(), el[1]->py(), el[1]->pz(), el[1]->energy());
    a_mee_ = (p0 + p1).M(); a_rho_ = rho; a_isOS_ = os; a_passTF_ = passTF; a_nJetTF_ = nTF;
    a_nJetGood_ = 0;
    for (size_t i = 0; i < alljets.size(); ++i) if (alljets[i].good) ++a_nJetGood_;
    treeA_->Fill();
  }
  if (!passTF) return;

  // ---------------- JetS
  std::vector<SelJet> sj;
  for (size_t i = 0; i < alljets.size(); ++i) if (alljets[i].good) sj.push_back(alljets[i]);
  std::sort(sj.begin(), sj.end(), byPt);
  if ((int)sj.size() < nJetsMin_) return;
  fillCut(4, true, true);

  // ---------------- DRC: |dR1 - dR2| < 0.2 (at least one of the two electrons)
  double dr1[2], dr2[2]; bool drc[2];
  for (int k = 0; k < 2; ++k) {
    std::vector<double> drs;
    for (size_t i = 0; i < sj.size(); ++i) drs.push_back(reco::deltaR(el[k]->eta(), el[k]->phi(), sj[i].eta, sj[i].phi));
    std::sort(drs.begin(), drs.end());
    dr1[k] = drs[0]; dr2[k] = drs[1];
    drc[k] = std::fabs(drs[0] - drs[1]) < dRdiff_;
  }
  if (!(drc[0] || drc[1])) return;
  fillCut(5, true, true);
  // ---------------- SG: opposite charge (SS = QCD control region)
  fillCut(6, os, ss);
  if (levelAOnly_) { if (selList_.is_open()) selList_ << run_ << ":" << evt_ << "\n"; return; }
  if (lazyHQ_) {   // HQ now (same cut as v2; JetS, DRC and SG do not depend on it)
    for (int k = 0; k < 2; ++k) {
      ctf[k] = el[k]->closestCtfTrackRef();
      hp[k] = ctf[k].isNonnull() && ctf[k]->quality(reco::TrackBase::highPurity);
    }
    if (!(hp[0] && hp[1])) return;
  }

  // (PV, run/lumi/event and electron ID were filled above, before the level-A tree)
  isOS_ = os; isSS_ = ss; passDRC_ = 1;
  e_pt_.clear(); e_eta_.clear(); e_phi_.clear(); e_dR1_.clear(); e_dR2_.clear(); e_q_.clear(); e_hp_.clear();
  e_drc_.clear(); e_sig_.clear(); e_ipp_.clear(); e_ippflip_.clear();
  j_pt_.clear(); j_eta_.clear(); j_phi_.clear(); j_emf_.clear();
  sv_x_.clear(); sv_y_.clear(); sv_z_.clear(); sv_chi2ndf_.clear(); sv_LT_.clear(); sv_L3D_.clear(); sv_LTsig_.clear();
  sv_k_.clear(); sv_kobjT_.clear(); sv_k3trk_.clear(); sv_k3obj_.clear(); sv_ptT_.clear(); sv_ptTobj_.clear();
  sv_mjj_.clear(); sv_mejj_.clear(); sv_ntrk_.clear(); sv_ele_.clear(); sv_j1_.clear(); sv_j2_.clear();
  sv_flags_.clear(); sv_hasEle_.clear(); sv_sig_.clear();
  g_pt_.clear(); g_eta_.clear(); g_phi_.clear(); g_vx_.clear(); g_vy_.clear(); g_vz_.clear(); g_id_.clear(); g_mid_.clear();
  for (size_t i = 0; i < sj.size(); ++i) { j_pt_.push_back(sj[i].pt); j_eta_.push_back(sj[i].eta); j_phi_.push_back(sj[i].phi); j_emf_.push_back(sj[i].emf); }

  // ---------------- truth: gen electrons; signal electron = daughter of the LW electron (|pdg| = lwPdg)
  bool sigEle[2] = {false, false};
  nSigEle_ = 0;
  if (!isData_) {
    edm::Handle<std::vector<PileupSummaryInfo> > pu;
    if (iEvent.getByLabel("addPileupInfo", pu) && pu.isValid())
      for (size_t i = 0; i < pu->size(); ++i) if ((*pu)[i].getBunchCrossing() == 0) nTrueInt_ = (*pu)[i].getTrueNumInteractions();
    edm::Handle<reco::GenParticleCollection> gps;
    if (iEvent.getByLabel("genParticles", gps) && gps.isValid())
      for (size_t i = 0; i < gps->size(); ++i) {
        const reco::GenParticle& g = (*gps)[i];
        if (std::abs(g.pdgId()) != 11 || g.status() != 1 || g.pt() < 10) continue;
        int mid = 0; const reco::Candidate* m = g.mother();
        while (m && m->pdgId() == g.pdgId()) m = m->mother();
        if (m) mid = m->pdgId();
        g_pt_.push_back(g.pt()); g_eta_.push_back(g.eta()); g_phi_.push_back(g.phi());
        g_vx_.push_back(g.vx()); g_vy_.push_back(g.vy()); g_vz_.push_back(g.vz());
        g_id_.push_back(g.pdgId()); g_mid_.push_back(mid);
        if (std::abs(mid) == lwPdg_)
          for (int k = 0; k < 2; ++k)
            if (reco::deltaR(g.eta(), g.phi(), el[k]->eta(), el[k]->phi()) < genMatchDR_ && g.charge() == el[k]->charge()) sigEle[k] = true;
      }
    nSigEle_ = int(sigEle[0]) + int(sigEle[1]);
  }

  // ---------------- SV reconstruction per electron x jet pair (80 < m_jj < 160 GeV)
  edm::ESHandle<MagneticField> bfield;
  iSetup.get<IdealMagneticFieldRecord>().get(bfield);
  const MagneticField* mf = bfield.product();

  std::vector<std::vector<reco::TrackRef> > jtrk(sj.size());
  for (size_t i = 0; i < sj.size(); ++i) {
    std::vector<reco::PFCandidatePtr> cs = sj[i].jet->getPFConstituents();
    for (size_t c = 0; c < cs.size(); ++c) {
      reco::TrackRef tr = cs[c]->trackRef();
      if (tr.isNull() || tr->pt() < trkPt_) continue;
      if (tr->hitPattern().numberOfValidHits() < trkMinHits_) continue;
      if (tr->hitPattern().numberOfValidPixelHits() < trkMinPix_) continue;
      jtrk[i].push_back(tr);
    }
  }
  for (int k = 0; k < 2; ++k) {
    reco::TransientTrack ett(ctf[k], mf);
    std::vector<std::set<unsigned> > seen;
    for (size_t a = 0; a < sj.size(); ++a) for (size_t b = a+1; b < sj.size(); ++b) {
      TLorentzVector ja(sj[a].px, sj[a].py, sj[a].pz, sj[a].e), jb(sj[b].px, sj[b].py, sj[b].pz, sj[b].e);
      double mjj = (ja + jb).M();
      if (mjj < mjjLo_ || mjj > mjjHi_) continue;
      std::vector<reco::TransientTrack> tts; tts.push_back(ett);
      std::vector<unsigned> tkey; tkey.push_back(ctf[k].key());
      std::set<unsigned> keys; keys.insert(ctf[k].key());
      size_t jj[2] = {a, b};
      for (int q = 0; q < 2; ++q) for (size_t t = 0; t < jtrk[jj[q]].size(); ++t) {
        const reco::TrackRef& tr = jtrk[jj[q]][t];
        if (keys.count(tr.key())) continue;
        keys.insert(tr.key()); tkey.push_back(tr.key());
        tts.push_back(reco::TransientTrack(tr, mf));
      }
      if ((int)tts.size() < svMinTrk_) continue;
      std::vector<FitV> vs = svra(tts);
      TLorentzVector e4(el[k]->px(), el[k]->py(), el[k]->pz(), el[k]->energy());
      double pox = el[k]->px() + sj[a].px + sj[b].px, poy = el[k]->py() + sj[a].py + sj[b].py, poz = el[k]->pz() + sj[a].pz + sj[b].pz;
      for (size_t v = 0; v < vs.size(); ++v) {
        const FitV& f = vs[v];
        // Table 2.1 of the thesis
        int n3 = 0; bool pairClose = false, pairWide = false, allLt = true, anyGt = false;
        double ptx = 0, pty = 0, ptz = 0;
        std::set<unsigned> sig;
        for (size_t t = 0; t < f.trk.size(); ++t) {
          const reco::Track& ta = tts[f.trk[t]].track();
          if (ta.p() > svTrkE_) ++n3;      // E ~ |p| for charged hadrons
          ptx += ta.px(); pty += ta.py(); ptz += ta.pz();
          sig.insert(tkey[f.trk[t]]);
          for (size_t u = t+1; u < f.trk.size(); ++u) {
            const reco::Track& tb = tts[f.trk[u]].track();
            double dr = reco::deltaR(ta.eta(), ta.phi(), tb.eta(), tb.phi());
            if (dr < dRclose_) pairClose = true;
            if (dr > dRwide_) pairWide = true;
            if (!(dr < dRmax_)) allLt = false;
            if (dr > dRmax_) anyGt = true;
          }
        }
        bool hasEle = (f.trk[0] == 0);
        int flags = 0;
        if ((int)f.trk.size() >= svMinTrk_) flags |= 1;
        if (n3 >= svMinTrk3_) flags |= 2;
        if (pairClose) flags |= 4;
        if (pairWide) flags |= 8;
        if (dRmaxMode_ == 1 ? anyGt : allLt) flags |= 16;
        bool good = (flags & 31) == 31;
        if (good) flags |= 32;
        if (!good || !hasEle) continue;   // store only selected SV associated to the electron
        bool dup = false; for (size_t s = 0; s < seen.size(); ++s) if (seen[s] == sig) dup = true;
        if (dup) continue;
        seen.push_back(sig);
        double x = f.v.x(), y = f.v.y(), z = f.v.z();
        double dx = x - pv->x(), dy = y - pv->y(), dz = z - pv->z();
        double LT = std::hypot(dx, dy), L3 = std::sqrt(dx*dx + dy*dy + dz*dz);
        double cxx = f.v.covariance(0,0) + pv->covariance(0,0), cyy = f.v.covariance(1,1) + pv->covariance(1,1),
               cxy = f.v.covariance(0,1) + pv->covariance(0,1);
        double sLT = LT > 0 ? std::sqrt(std::max(0., dx*dx*cxx + 2*dx*dy*cxy + dy*dy*cyy))/LT : 0;
        sv_x_.push_back(x); sv_y_.push_back(y); sv_z_.push_back(z);
        sv_ntrk_.push_back(f.trk.size()); sv_chi2ndf_.push_back(f.chi2ndf);
        sv_LT_.push_back(10.*LT); sv_LTsig_.push_back(sLT > 0 ? LT/sLT : 0); sv_L3D_.push_back(10.*L3);
        sv_k_.push_back(10. * (dx*ptx + dy*pty));                 // thesis: transverse, P_T = sum of SV track pT
        sv_kobjT_.push_back(10. * (dx*pox + dy*poy));             // transverse, P_T of e + j + j
        sv_k3trk_.push_back(10. * (dx*ptx + dy*pty + dz*ptz));    // 3D, tracks
        sv_k3obj_.push_back(10. * (dx*pox + dy*poy + dz*poz));    // 3D, objects
        sv_ptT_.push_back(std::hypot(ptx, pty)); sv_ptTobj_.push_back(std::hypot(pox, poy));
        sv_mjj_.push_back(mjj); sv_mejj_.push_back((e4 + ja + jb).M());
        sv_ele_.push_back(k); sv_j1_.push_back(a); sv_j2_.push_back(b);
        sv_flags_.push_back(flags); sv_hasEle_.push_back(hasEle); sv_sig_.push_back(sigEle[k]);
      }
    }
  }

  // ---------------- IPP (thesis): an electron with >=1 SV with kappa<0 and |P_T|>20 GeV, and every
  // other SV of that electron with L_T > 0.02 mm.  'flip': kappa -> -kappa for SVs of a truth-matched
  // signal electron (thesis convention for the causal signal sample).
  bool ipp = false, ippf = false;
  for (int k = 0; k < 2; ++k) {
    bool ok[2] = {false, false};
    for (int fl = 0; fl < 2; ++fl) {
      double sgn = (fl == 1 && sigEle[k]) ? -1. : 1.;
      for (size_t v = 0; v < sv_k_.size(); ++v) {
        if (sv_ele_[v] != k) continue;
        if (!(sgn * sv_k_[v] < 0 && sv_ptT_[v] > ippPT_)) continue;
        bool others = true;
        for (size_t u = 0; u < sv_k_.size(); ++u) if (u != v && sv_ele_[u] == k && !(sv_LT_[u] > ippLT_)) others = false;
        if (others) { ok[fl] = true; break; }
      }
    }
    e_ipp_.push_back(ok[0]); e_ippflip_.push_back(ok[1]);
    ipp = ipp || ok[0]; ippf = ippf || ok[1];
    e_pt_.push_back(el[k]->pt()); e_eta_.push_back(el[k]->eta()); e_phi_.push_back(el[k]->phi());
    e_q_.push_back(el[k]->charge()); e_hp_.push_back(hp[k]); e_dR1_.push_back(dr1[k]); e_dR2_.push_back(dr2[k]);
    e_drc_.push_back(drc[k]); e_sig_.push_back(sigEle[k]);
  }
  passIPP_ = ipp; passIPPflip_ = ippf;
  if (ipp) fillCut(7, os, ss);
  tree_->Fill();
}

DEFINE_FWK_MODULE(WDVQCDAnalyzer);
