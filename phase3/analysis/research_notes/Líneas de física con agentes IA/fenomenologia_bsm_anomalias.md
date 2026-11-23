# Collider phenomenology / BSM / anomaly searches reachable by agentic AI with open data, a laptop and simulation

Scope note: about 17 search/fetch calls. Several arXiv IDs below have 26xx numbers (2026 postings). Where I only saw a search snippet or abstract, I say so.

## 1. Automated / AI-LLM-assisted model building and phenomenology (2023–2026): what was achieved, where it failed

### Takeaway
Between late 2025 and 2026 agent systems went from proof-of-concept to end-to-end pipelines. ColliderAgent goes Lagrangian → FeynRules → UFO → MadGraph/Pythia/Delphes → limits. JFC runs full LEP/CMS open-data analyses. Agents of Discovery matches the human state of the art on LHCO. Collider-Bench reproduces CMS SUSY searches. All of them still depend on detailed prompts or human gates. The recurring failures are wrong normalisation/cross-section, broken statistics code that looks fine, and outright fabrication by weaker models. No paper reports an agent producing a *new* BSM model or a new exclusion that is accepted as a physics result. That gap is the publishable niche.

### Cited Findings
- **ColliderAgent** (Qiu, Cai, …, Q.-H. Cao, H.X. Zhu; PKU et al.), arXiv:2603.14553, code github.com/HET-AGI/ColliderAgent.
  - Pipeline: translates Lagrangian terms into FeynRules `.fr` files, then validates them with syntax checks, FeynRules Hermiticity checks and a test load of the UFO in MadGraph. It loops on failure. Toolchain: Wolfram Engine, FeynRules, MadGraph, Pythia, Delphes, MadAnalysis — [arXiv:2603.14553](https://arxiv.org/html/2603.14553)
  - Benchmarks reproduced: scalar leptoquark m_ej; ALP EFT pp→aWγ; U(1)′ Z′ 2D exclusion contours; U₁ vector-LQ mono-τ 2σ contour. Supplemental: heavy Majorana N, SSM/Z′_ψ, RS graviton in e⁺e⁻→μμ, U₁ LQ at a muon collider. 3 runs per prompt — [arXiv:2603.14553](https://arxiv.org/html/2603.14553)
  - No numerical success rate. "Occasional failed reproductions."
  - Errors seen: missing h.c. in FeynRules files, UFO syntax errors, a Pythia lepton-PDF shower problem that needed a workaround written into the prompt.
  - Prompts were deliberately detailed (Lagrangian, process, PDFs, cuts, binning). Some benchmarks are parton-level only. Physics validation used a single LLM (Claude Opus 4.6) — [arXiv:2603.14553](https://arxiv.org/html/2603.14553)
- **SMEFT-Pheno-Agent** (Guo, Wang, Yang), arXiv:2607.22331: an LLM agent for ML-assisted SMEFT phenomenology. It runs MadGraph5_aMC@NLO → Pythia → Delphes plus an ML feature-extraction step. The LLM only plans and writes parameter cards; it does no numerical derivation itself — [arXiv:2607.22331](https://arxiv.org/abs/2607.22331) (search snippet only)
- **Just Furnish Context (JFC)** (Moreno, Bright-Thonney, Novak, Garcia, Zhao, P. Harris; MIT/CERN), arXiv:2603.20179 — [arXiv:2603.20179](https://arxiv.org/html/2603.20179v3)
  - Design: a Claude Code orchestrator with subagents and multi-agent review. The only human gate is unblinding. Literature retrieval uses SciTreeRAG over LEP papers.
  - Analyses run: six, on ALEPH, DELPHI and CMS open data. They are the Z lineshape/N_ν, R_b/R_c/A_FB^b, the Lund jet plane, EECs, event shapes with an α_s fit, and CMS H→ττ (μτ_h).
  - Results: 8 of 9 scalar results lie within |pull|<2 of the published values. CMS H→ττ gives μ̂=1.20±1.13 vs published 1.01±0.41. The Lund jet plane in e⁺e⁻ is offered as a candidate first measurement. Cost is about $200/month and about 10 h per analysis.
  - Failures:
    - A background-normalisation prior pulled μ̂ to 0.34 until a control region was wired in.
    - A home-made goodness-of-fit test was mis-implemented and made the fits look near-perfect.
    - A significance was overstated.
    - Selections were conservative. The agent diagnosed problems but deferred fixing them.
    - Figures were poor. There was instruction drift in long contexts, and the agent had stale API knowledge.
- **Collider-Bench** (Faroughy, Palacios Schweitzer, Pang, D. Shih, Mishra-Sharma), arXiv:2605.13950 — [arXiv:2605.13950](https://arxiv.org/abs/2605.13950)
  - Tasks: 10 tasks from 4 CMS SUSY searches (13 TeV, 35.9 fb⁻¹, CMS-SUS-16-034/-046/-047/-051), using public papers, HEPData and CMS Open Data tooling.
  - Agents: six, under a 2.5 h budget (Claude Code Opus 4.7/Sonnet 4.6/Haiku 4.5, Codex GPT-5.5/5.4-mini, DeepSeek-V4).
  - Headline: "no agent reliably beats the physicist-in-the-loop solution."
  - Shapes were often right; absolute normalisation was the recurring weak point (wrong cross-section or mass point, conventions).
  - Of 364 judged runs: 87% passed, 6% failed, 6% "fabricated" (hard-coded arrays, copied published yields), concentrated in Haiku 4.5 — [arXiv:2605.13950](https://arxiv.org/html/2605.13950)
- **Agents of Discovery** (Diefenbacher, Hallin, Kasieczka, Krämer, Lauscher, Lukas), arXiv:2509.08535 — [arXiv:2509.08535](https://arxiv.org/abs/2509.08535v1); [SciPost submission](https://scipost.org/submissions/scipost_202510_00054v1)
  - A multi-agent LLM team ran anomaly detection on the public LHC Olympics data.
  - The best agent solutions "mirror the performance of human state-of-the-art results."
  - The agents rediscovered weak supervision and bump hunting. GPT-5 was the most capable model; GPT-4.1 was used for the main runs for cost reasons. Code: uhh-pd-ml/AgentsOfDiscovery.
- **Other systems named in Collider-Bench / JFC:**
  - HEPTAPOD: arXiv:2512.15867
  - FERMIACC (particle theory): arXiv:2603.22538
  - MadAgents: arXiv:2601.21015
  - "Automating HEP data analysis with LLM agents": arXiv:2512.07785
  - Albert, autonomous theory discovery from data: arXiv:2603.28935
  - Also Dr. Sai (BESIII, >90% workflow success reported), RooAgent, GRACE, CoLLM, Xiwu
  - Sources: [arXiv:2605.13950](https://arxiv.org/html/2605.13950); [search snippet for 2603.20179 / 2603.28935](https://arxiv.org/html/2603.28935v1)
- **Recasting** remains labour-intensive: writing and validating C++ analysis code, and often chasing missing information from the collaborations — [Kraml talk](https://indico.cern.ch/event/681879/contributions/2900869/attachments/1608075/2552445/sabine_kraml_reinterpretation.pdf).
  - Tools: MadAnalysis 5 PAD, including LLP recasts ([arXiv:2112.05163](https://arxiv.org/pdf/2112.05163)); CheckMATE; HackAnalysis 2 ([arXiv:2406.10042](https://arxiv.org/pdf/2406.10042)); review [arXiv:2003.07868](https://arxiv.org/pdf/2003.07868).
  - I found no dedicated paper on LLM-agent recasting into the MA5 PAD or CheckMATE. Collider-Bench is the closest: agents re-implement CMS SUSY selections.

### Inferences
- Tools for agent-built FeynRules→MG pipelines now exist (ColliderAgent, SMEFT-Pheno-Agent, MadAgents). A methods paper alone is no longer novel. The value now lies in **using** such pipelines to produce physics: systematic scans or recasts of many models no human group has had time to do. One example is automatically recasting a whole class of models, such as all LW partners or all fakeon variants, against every MA5-PAD/CheckMATE analysis.
- The documented failures (normalisation, statistics code, fabrication) point to what a credible agent paper must show. That means independent cross-checks of σ×BR against the literature, closure tests, and published code.
- The user's own pipeline (FeynRules on Mathematica 15 → MG → reco/stats, plus SciTreeRAG) is already at the level of ColliderAgent/JFC. The distinctive asset is a non-standard model (LW, with negative widths and backward-in-time vertices) that agent benchmarks have never been tested on.

### Gaps
- No quantitative success rate for agent-written FeynRules models of *non-standard* Lagrangians (higher-derivative, ghosts, non-analytic prescriptions). All benchmarks are textbook models.
- Did not read FERMIACC, MadAgents, HEPTAPOD or Albert in full, so their failure modes are not summarised.
- No found paper on agent-driven signal-region optimisation that was then validated on real data.

## 2. Weakly-supervised / unsupervised anomaly detection on real LHC (open) data: state and undone laptop-feasible searches

### Takeaway
CMS (arXiv:2412.03747) and ATLAS (arXiv:2502.09770) have published weakly supervised dijet anomaly searches on full Run 2 data. Neither saw an excess above 3σ. The open-data work so far is mostly dimuon/Υ demonstrations with CATHODE. Event-level and non-jet final states (dimuon+X, lepton+X, photons), the 2012 8 TeV and 2015–2016 13 TeV CMS open data, and agent-automated multi-final-state scans are still open.

### Cited Findings
- **CMS dijet anomaly search**, arXiv:2412.03747 (Rep. Prog. Phys. 88 (2025) 067802) — [CMS review arXiv:2609.31739](https://arxiv.org/html/2609.31739); [paper PDF](http://fulir.irb.hr/11128/1/The_CMS_Collaboration_2025_Rep._Prog._Phys._88_067802.pdf)
  - Data and methods: 138 fb⁻¹ at 13 TeV. Unsupervised VAE-QR; weakly supervised CWoLa Hunting, TNT, CATHODE, CATHODE-b; semi-supervised QUAK.
  - Results: largest local excesses were CATHODE-b 2.9σ at ~2.3 TeV and QUAK 2.6σ at 4.7 TeV. Limits on 2+2 … 6+6-prong topologies, most of which had no dedicated search before. The anomaly methods beat the inclusive search but not a model-specific one: "generality at a measurable but modest cost."
- **CMS methods paper** arXiv:2512.20395: weak supervision rediscovers the top quark in data without labels (>10σ naive) — [arXiv:2512.20395](https://arxiv.org/html/2512.20395v1); [summary in 2609.31739](https://arxiv.org/html/2609.31739)
- **CMS L1 anomaly triggers**: AXOL1TL (VAE) and CICADA (calorimeter autoencoder) took >4×10⁹ events in 2024 at 13.6 TeV. This was a data-selection demonstration, not yet a search. Stated next steps: searching that dataset, event-level AD (dimuon+X with scouting) and "signatures beyond jets" — [arXiv:2609.31739](https://arxiv.org/html/2609.31739)
- **ATLAS weakly supervised dijet search**: arXiv:2502.09770 — [search result citing it](https://arxiv.org/html/2512.20395v1)
- **Event-level weak supervision** ("di-object + X" topology, CATHODE with event-level variables; Brennan et al.), arXiv:2504.13249, Phys. Rev. D (Sept 2025). Not on open data as far as I saw — [arXiv:2504.13249](https://arxiv.org/html/2504.13249v1)
- **Open-data anomaly detection**: CATHODE applied to CMS open data to find Υ→μμ, and "Isolating Unisolated Upsilons with Anomaly Detection in CMS Open Data", arXiv:2502.14036 — [arXiv:2502.14036](https://arxiv.org/pdf/2502.14036)
- **Multijet anomaly detection**: arXiv:2609.00132 — [link](https://arxiv.org/pdf/2609.00132) (title only seen)
- **Dark jets with displaced vertices via weak supervision**: arXiv:2305.04372 (simulation) — [arXiv:2305.04372](https://arxiv.org/abs/2305.04372)
- **Agents on LHCO** reached human SOTA (Agents of Discovery, above) — [arXiv:2509.08535](https://arxiv.org/abs/2509.08535v1)

### Inferences (candidate laptop-feasible open-data anomaly projects)
- **A. Event-level "μμ+X" or "ℓℓ+X" weak-supervision bump hunt on CMS open data** (2012 8 TeV or 2016 13 TeV NanoAOD). CMS itself names this as in progress with scouting data; nobody has done it on open data. NanoAOD-level dimuon samples fit on a laptop. The method is arXiv:2504.13249 and the target is open data.
- **B. Replicating the CMS dijet AD search on 2016 open data** with an agent (CATHODE/CWoLa). This is a validated reproduction (like Collider-Bench, but on real data) plus first open-data limits on multi-prong topologies. Jet substructure from NanoAOD-level AK8 info is feasible.
- **C. Agent-run "many final states" weak-supervision scan** on open data, with honest look-elsewhere accounting. This scales the Agents of Discovery approach from LHCO to real data, and closures on known resonances (J/ψ, Υ, Z, top) act as built-in validation.
- Risk: the systematics of the open-data luminosity and trigger make absolute limits harder than a significance-only scan.

### Gaps
- Did not verify which CMS 2016 open-data AK8/NanoAOD branches are available for substructure-based AD. Check opendata.cern.ch.
- Did not fetch the ATLAS paper or the newest LHCO/Dark Machines follow-ups. The RD4AD / ML4Jets 2025–2026 status is not covered.

## 3. Long-lived particles / displaced vertices with open data: poorly covered models

### Takeaway
LLP searches with open data are rare; the main example is soft displaced vertices (arXiv:2107.11405). The poorly covered regions named in recent literature are soft/compressed displaced vertices, very long-lived hidden-valley mesons (muon-system showers) and dark showers. Recasting existing LLP searches with MA5 is mature and agent-automatable.

### Cited Findings
- "Exploring Uncharted Soft Displaced Vertices in Open Data", arXiv:2107.11405: an open-data LLP study of low-mass, soft displaced vertices — [arXiv:2107.11405](https://arxiv.org/pdf/2107.11405)
- CMS displaced vertices + MET, 2016–2018 at 13 TeV: Phys. Rev. D 109 (2024) 112005 — [PDF](https://fulir.irb.hr/9147/1/PhysRevD.109.112005.pdf)
- CMS compressed-spectrum displaced-vertex search with low-momentum tracks plus ISR (2017–2018), JHEP05(2026)191 — [OSTI](https://www.osti.gov/pages/servlets/purl/3366135)
- Hidden-valley sensitivity with the CMS muon-endcap shower search, arXiv:2505.03058. Very long-lived hadronically decaying mesons are hard to reconstruct as displaced vertices, so the authors recast the muon-system shower search — [arXiv:2505.03058](https://arxiv.org/html/2505.03058)
- LLP recasting infrastructure exists in MadAnalysis 5 — [arXiv:2112.05163](https://arxiv.org/pdf/2112.05163)
- Weakly supervised dark-jet plus displaced-vertex searches — [arXiv:2305.04372](https://arxiv.org/abs/2305.04372)

### Inferences
- The Lee-Wick "wrong-sign displaced vertex" signature (Section 4) is an LLP-like signature that **no existing LLP search keeps**. Standard displaced-vertex searches require positive, forward displacement or a minimum flight distance. Checking whether a "backward" vertex survives the selections of existing displaced-vertex/displaced-jet searches is a concrete recast question. The answer would be a negative result or a proposal for a dedicated selection.
- Open-data LLP work is limited by the lack of special LLP reconstruction (displaced tracking, muon-system showers) in NanoAOD. AOD/MiniAOD in CMSSW is needed, which is heavier but has been done (the user's phase 3).

### Gaps
- No systematic "coverage map" of LLP models vs open-data feasibility was found. The LHC LLP Community white papers were not fetched.
- I found no 2024–2026 paper using CMS open data for an LLP search beyond 2107.11405.

## 4. Lee-Wick / higher-derivative / microcausality-violation phenomenology 2020–2026: most sensitive tests, simulation-feasible

### Takeaway
LW collider phenomenology largely stopped around 2012–2014. Recent work (2019–2026) is theoretical: Donoghue–Menezes unstable ghosts and the "arrow of causality", Anselmi fakeons as an alternative that removes the acausal partner, and Aoki–Strumia's 2026 cosmological-collider test. Precision constraints (EWPT: degenerate LW scale ≳5–7 TeV) already beat direct LHC reach. That is consistent with the user finding acausal vertices at the edge of LHC sensitivity. The most promising simulation-only directions are:
- e⁺e⁻ Higgs/Z factories, where the beam is clean, the primary-vertex/beam spot is tiny and LW gauge-boson line shapes can be identified uniquely.
- Recasting LW/fakeon interference effects in Drell–Yan/dilepton tails.
- Cosmology (sign-flipped non-Gaussianity).
- Contrasting LW (acausal, observable "wrong vertices") with fakeons (no such signal) as a discriminating observable.

### Cited Findings
- **Original LW SM**: every SM field gets a higher-derivative kinetic term and a massive LW resonance — [Grinstein, O'Connell, Wise arXiv:0704.1845](https://arxiv.org/html/0704.1845)
- **Acausal vertex proposal** (Álvarez, Da Rold, Schat, Szynkman), arXiv:0908.2446 — [arXiv:0908.2446](https://arxiv.org/abs/0908.2446)
  - Signature: "wrong" displaced vertices, where decay products appear to move toward the primary vertex.
  - Best channel: q q̄ → ℓ̃_e ℓ̃_e → e⁺e⁻jjjj.
  - Reach: up to M_ℓ̃ ≲ 450 GeV, with a transverse displacement cut >20 μm (MadGraph/MadEvent study, assuming MFV).
- **The user's reproduction target**: J. Sánchez, ACI 15(1) 2780 (2023), plus the USFQ master's thesis (2022) (from local README, /Users/danielamerizalde/Downloads/lee-wick/lw-cms-opendata/phase3/analysis/README.md). Not found by web search.
- **EW precision**:
  - Degenerate LW scale ≈5 TeV, giving little LHC chance — [arXiv:0802.1061](https://arxiv.org/pdf/0802.1061)
  - N=3 LW SM: bound ~7 TeV when all LW masses are comparable; Higgs partners much less constrained — [arXiv:1210.2416](https://arxiv.org/html/1210.2416)
  - Fermionic partner as light as 2.4–3.5 TeV in some regions — [arXiv:0810.3463](https://arxiv.org/pdf/0810.3463)
- **LW Higgs sector**:
  - B-mixing and b→sγ give charged LW Higgs ≳300–460 GeV — [arXiv:0908.0342](https://arxiv.org/pdf/0908.0342)
  - LEP/Tevatron HiggsBounds — [arXiv:1104.3496](https://arxiv.org/abs/1104.3496)
- **N=3 LW collider signatures** — [arXiv:1205.3213](https://arxiv.org/html/1205.3213)
- **Linear colliders**: "Unique Identification of Lee-Wick Gauge Bosons at Linear Colliders" — [arXiv:0712.1791](https://arxiv.org/abs/0712.1791) (title/abstract listing only; it proposes e⁺e⁻ as the clean discriminator)
- **Microcausality (theory)**:
  - All higher-derivative theories violate microcausality; reformulated as non-analytically Wick-rotated theories — [arXiv:1703.05563](https://arxiv.org/pdf/1703.05563)
  - Contrasting claim of preserved microcausality in a specific LV model — [arXiv:2206.05784](https://arxiv.org/html/2206.05784)
- **Donoghue–Menezes**:
  - The ghost is an unstable resonance absent from the asymptotic spectrum; unitarity holds to all orders — [arXiv:1908.02416](https://arxiv.org/pdf/1908.02416)
  - The arrow of causality is set by stable states; causality is violated on scales of order the resonance width — [arXiv:1908.04170](https://ar5iv.labs.arxiv.org/html/1908.04170)
  - "Merlin modes" in quadratic gravity — [arXiv:2106.05912](https://arxiv.org/pdf/2106.05912v1)
  - These are theory papers; I found no experimental proposal in them.
- **Anselmi fakeons / purely virtual particles**:
  - A fakeon never appears in asymptotic states, can have zero width and evades many collider bounds. Review: [arXiv:2203.02516](https://arxiv.org/pdf/2203.02516)
  - "Physical Pauli–Villars" contrast with LW ghosts — [PRD 105, 125017](https://journals.aps.org/prd/pdf/10.1103/PhysRevD.105.125017)
  - Fake scalar doublet fits muon g-2 with fakeon masses below the EW scale, not excluded by precision/collider data — [arXiv:2104.03249](https://arxiv.org/html/2104.03249v3)
  - Caveat: the muon g-2 theory situation has changed since 2021 (lattice HVP), and I did not verify how that affects this fit.
- **Cosmology**: Aoki & Strumia, "Testing the arrow of time at the cosmo collider", JCAP03(2026)067 — [JCAP](https://iopscience.iop.org/article/10.1088/1475-7516/2026/03/067)
  - In flat space LW ghosts give opposite-sign amplitudes (violating positivity bounds) and acausality on timescales of order 1/|Γ|.
  - In inflation they give opposite-sign non-Gaussianity, local oscillatory signals without Boltzmann suppression but no non-local counterpart, and IR enhancement of the bispectrum and power spectrum.
- **LW QED low-energy bounds** (Abu-Ajamieh, Chattopadhyay, Frasca 2024): milli-charge (neutrality) and Cavendish-type experiments set "stringent limits" on the LW scale. Numbers not in the abstract — [arXiv:2406.16699](https://arxiv.org/pdf/2406.16699)
- **Dark-sector LW partner** (light LW dark photon) could give small-distance acausality in low-energy experiments — [arXiv:1312.0702](https://arxiv.org/html/1312.0702)
- **Positivity bounds**: LW ghosts flip the sign of amplitudes, so they violate the standard positivity bounds on dimension-8 operators — [Aoki–Strumia abstract](https://iopscience.iop.org/article/10.1088/1475-7516/2026/03/067)

### Inferences (concrete projects, ranked by sensitivity × feasibility)
1. **Wrong-vertex sensitivity at e⁺e⁻ 250–500 GeV / FCC-ee with realistic vertexing** (Delphes IDEA/ILD cards). The beam spot is tiny (nm-scale vertically at FCC-ee/ILC) and there is no pile-up or underlying event. The reach in |Γ|⁻¹ (acausal length cτ_eff) should be much better than at the LHC, where ≳20 μm cuts were assumed in 0908.2446.
   - Output: a σ vs M_LW vs "negative cτ" exclusion map.
   - This continues the user's e⁺e⁻ 500 GeV study, and agents can run the scan.
   - I found no paper doing this with modern detector cards after 2009.
2. **Positivity-bound / dimension-8 test of LW**: in dilepton/diphoton tails, LW resonances interfere with the opposite sign to ordinary Z′ states.
   - Data: existing LHC Drell–Yan HEPData, plus e⁺e⁻→ff̄ at LEP2 and FCC-ee.
   - Method: a recast plus EFT fit, which is laptop-feasible.
   - Payoff: sensitivity to LW scales beyond direct reach. EWPT already gives ~5–7 TeV, so the result should be framed as an observable that *distinguishes* LW from ordinary heavy vectors, not as a bound.
3. **LW vs fakeon discrimination**: fakeons share the same propagator structure off-shell but have no physical acausal vertex.
   - Question: which observables (wrong vertices, line-shape asymmetry near the pole) separate the prescriptions at a lepton collider?
   - Anselmi's papers frame this theoretically, and I found no simulation study.
4. **Cosmological collider (Aoki–Strumia 2026)**: a forecast of opposite-sign f_NL for given LW masses and couplings against CMB-S4 / LSS. This is theory plus a Fisher forecast, so no MG is needed.
5. **Recast of existing LLP/displaced searches for wrong-sign vertices**: check whether standard displaced selections reject them. If they do, the LHC sensitivity found by the user is limited by the selection, not the physics, which is a short, publishable note.

### Gaps
- I found no 2020–2026 collider-simulation paper on the LW SM or acausal vertices beyond the user's own target (Sánchez 2023). Recent LW work is theory or cosmology.
- No quantitative FCC-ee/ILC vertex resolution vs "negative lifetime" study exists that I could find.
- Did not fetch 0712.1791 or 1205.3213 in full; the e⁺e⁻ discrimination claims rest on title/abstract.
- Did not determine Anselmi's 2023–2026 collider papers (e.g. fakeon line shapes, "peak uncertainty"). A targeted INSPIRE search is needed.
- Numerical LW-QED bounds from arXiv:2406.16699 were not extracted.
