# LLM agents for reproducing, validating and reinterpreting published LHC analyses with public data and tools

Research date: 2026-11-17. Sources are mostly 2024–2026. Where a claim comes only from a search snippet and not from the fetched page, it is marked "(snippet)".

## 1. Status of open data (CMS, ATLAS, LHCb, HEPData) and what fits on a laptop

### Takeaway
CMS now has NanoAOD for 2016 (13 TeV). NanoAOD is a flat ROOT tree that does not need CMSSW, so most prompt-object analyses (leptons, jets, MET) run on a laptop. 2010–2015 data need CMSSW (AOD/MiniAOD) in Docker, with POET-style skimming first. ATLAS released 36 fb⁻¹ of 13 TeV data in PHYSLITE format for research in July 2024, plus HepMC generator output. LHCb works through an on-demand Ntupling Service rather than bulk files. HEPData holds more than 10,000 records but only around 41 full statistical models. Analyses of displaced or long-lived particles are the weak spot of every open format.

### Cited Findings
- CMS released its first 13 TeV pp data (2016) in August 2024. The release covers more than 70 TB of collision data and 830 TB of simulation, with more than 20,000 simulated processes. Everything is in MiniAOD, a subset of the data is also in an expanded NanoAOD with PF candidates, and all data and MC are in NanoAOD. — [CERN Open Science, "CMS releases 13 TeV proton collision data from 2016"](https://openscience.web.cern.ch/node/441); [CMS news](https://cms.cern/node/2201)
- According to CMS, NanoAOD cuts file size by about 95%. Because the files are ROOT trees, analysing them "does not require the use of CMSSW or CMS open data environments" (snippet). — [CMS news](https://cms.cern/node/2201)
- Release timeline: 2015 data as MiniAOD (December 2021). 2016 as Ultra-Legacy MiniAOD+NanoAOD (2024). A partial 2017 release was planned for 2025, with the aim of finishing Run 2 by 2030 alongside the first Run 3 data (snippet from a 2025 talk). — [J. Hogan, "Ten years of CMS Open Data", EPS-HEP 2025](https://indico.in2p3.fr/event/33627/contributions/154922/attachments/95280/145852/TenYrsCMSOD_EPS2025_JHogan%20(1).pdf); [CERN Open Data, CMS about](https://opendata.cern.ch/about/cms). I could not confirm that the 2017 release actually came out (see Gaps).
- All CMS open data is released under CC0. — [CMS news](https://cms.cern/node/2201)
- ATLAS: the first research open data came out in July 2024. It is 36 fb⁻¹ of 13 TeV pp data (2015–2016) in PHYSLITE format. Heavy-ion data followed (486 μb⁻¹ minimum bias). The DPHEP 2026 report counts more than 12 billion generator events in more than 6,000 datasets at 13 and 13.6 TeV, in HepMC text format. — [arXiv:2502.21133, "Open Data at ATLAS"](https://arxiv.org/pdf/2502.21133); [CERN Open Science, "ATLAS releases 65 TB of open data for research"](https://openscience.web.cern.ch/node/439); [DPHEP Global Report 2026, arXiv:2607.06775](https://arxiv.org/pdf/2607.06775)
- The 2025 ATLAS 13 TeV release (beta, July 2025, 36 fb⁻¹) is a simplified format for education. ATLAS itself points research users to the research release. — [ATLAS 13 TeV 2025 Data — Beta](https://opendata.atlas.cern/docs/data/for_education/13TeV25_details)
- ATLAS says it aims for data that is "analysable on older commodity hardware". This is a goal, not a verified property of PHYSLITE. — [opendata.atlas.cern/about us](https://opendata.atlas.cern/docs/aboutus)
- LHCb: all Run 1 data (~1 PB) is on the portal. For Run 2 it uses the Ntuple Wizard plus an Ntupling Service, which produces ntuples on demand through Analysis Productions and publishes them on the portal (alpha inside the collaboration in February 2024, external beta at a workshop on 22 October 2024). — [Fitzgerald, DPHEP 2024](https://indico.cern.ch/event/1432766/contributions/6096205/attachments/2939597/5182164/Fizgerald_LHCb_DPHEP2024_final.pdf); [CERN Open Data: LHCb service for Run 2](https://opendata.cern.ch/docs/lhcb-releases-service-to-access-run2-data); [arXiv:2302.14235](https://arxiv.org/abs/2302.14235v1)
- HEPData has "more than 10,000 publication records". Total open data volume is about 5 PB. Searching HEPData for full statistical models finds only 41 (16 SUSY, 21 top). — [LHC Reinterpretation Forum, arXiv:2504.00256 §3.1, §3.3, §3.7](https://arxiv.org/html/2504.00256v1)
- The Reinterpretation Forum says LLP analyses are hard with current open-data formats and that "more work is needed". — [arXiv:2504.00256 §3.1, §3.5](https://arxiv.org/html/2504.00256v1)
- Precedent for displaced-vertex work on CMS 8 TeV open data: An et al. searched for soft displaced vertices from compressed top partners with 11.6 fb⁻¹ at 8 TeV. — [arXiv:2107.11405](https://arxiv.org/abs/2107.11405)

### Inferences
- What runs on a laptop: (a) analyses of 2016 NanoAOD with prompt objects (RDataFrame, coffea or uproot), (b) skims of 2010–2012 AOD with POET in Docker as long as the skim is restricted to a few datasets (as in the Sánchez case), and (c) ATLAS PHYSLITE for medium-sized analyses. Anything that needs tracks or vertices beyond what NanoAOD stores (displaced vertices, re-reconstruction) forces AOD/MiniAOD plus the experiment's software, which takes longer and uses more disk.
- The LLP gap in NanoAOD is exactly the area where the researcher's case study (displaced vertices in AOD 2012 with CMSSW 5_3_32) shows something rare: an agent that can handle legacy CMSSW, not just flat ntuples.

### Gaps
- I did not confirm whether the partial CMS 2017 release happened, or its contents. I also did not verify the exact number of ATLAS research papers using PHYSLITE.
- I did not find a public benchmark of PHYSLITE or NanoAOD analysis time on a laptop.

## 2. Reinterpretation infrastructure and bottlenecks an agent could remove

### Takeaway
The ecosystem is mature but depends on people. Rivet dominates measurements. CheckMATE, MadAnalysis 5 (PAD), HackAnalysis, ColliderBit and SimpleAnalysis cover searches at reconstruction level. SModelS covers simplified models. pyhf/HS3 is the route for full likelihoods. The bottlenecks the community itself names are a small, unsustainable pool of maintainers, information lost once analysis teams disband, few full statistical models, and LLP analyses that are hard to recast. Agents are already starting to be used to write recasts (MadAgents, Collider-Bench).

### Cited Findings
- The forum's own report: preservation "relies on the goodwill of a relatively small number of dedicated individuals. This model is not sustainable". The reproducibility of "several LHC Run-1 and even Run-2 searches … have already been lost within ATLAS and CMS". — [arXiv:2504.00256, §1 and §4](https://arxiv.org/html/2504.00256v1)
- Missing information is "very difficult to retrieve" once the analysis team has disbanded. Some key ingredients "are missing, even to the collaborations". — [arXiv:2504.00256 §3.3–3.4](https://arxiv.org/html/2504.00256v1)
- Coverage numbers: a HEPData query on 27 March 2025 returned 1,117 records with Rivet, MadAnalysis or CheckMATE codes, most of them Rivet only. 479 of these come from the LHC experiments (245 ATLAS, 142 CMS, 48 LHCb, 44 ALICE), which is "just over 22%" of LHC records. SimpleAnalysis covers 56 searches, mostly SUSY. — [arXiv:2504.00256 §3.5](https://arxiv.org/html/2504.00256v1)
- Incentive: publications with reusable analysis logic receive 22% more citations (2016–2022) and 62% more (2016–2024). For BSM searches the figures are 40% and 90%. — [arXiv:2504.00256 §3.5, Figs. 3–4](https://arxiv.org/html/2504.00256v1)
- Recommendations: publish full statistical models as standard practice (pyhf, HS3), add run cards and ML models (ONNX) to HEPData, and plan for preservation from the design stage. The document does not mention LLMs. — [arXiv:2504.00256 §3.3, §3.5, §3.7](https://arxiv.org/html/2504.00256v1)
- Previous status report (2020): per-object efficiency maps generalise better than benchmark-model parametrisations, and no standard yet existed for high-dimensional maps on HEPData. — [arXiv:2003.07868 / SciPost Phys. 9, 022](https://scipost.org/SciPostPhys.9.2.022)
- The 9th RIF workshop (CERN, 25–28 February 2025) marked the transition from the RIF to the LHC Reinterpretation (REI) Working Group. — [Indico 1466101](https://indico.cern.ch/event/1466101/) (snippet)
- SModelS v3 goes beyond Z2 topologies and added spin-1 resonance searches. The current database is v3.1.1 (Zenodo, February 2026). — [SModelS v3, SUSY 2024 talk](https://indico.cern.ch/event/1354279/contributions/5950353/attachments/2873322/5031739/smodels-v3-going-beyond-z2-topologies-SUSY-2024.pdf); [Zenodo 18479750](https://zenodo.org/records/18479750) (snippet; analysis count not confirmed)
- MadAnalysis 5 PAD: as of 2022, 4 ATLAS and 5 CMS recasts supported signal-region combination with full or simplified likelihoods. — [arXiv:2206.14870](https://arxiv.org/pdf/2206.14870)
- HackAnalysis (Goodsell) was created because the large frameworks were "monolithic" and hard to extend for LLPs. It started with the CMS disappearing-track recast, v2 added electroweakino analyses, and its LLP routines were also ported to MA5. — [arXiv:2106.08815](https://web3.arxiv.org/pdf/2106.08815); [arXiv:2406.10042 (HackAnalysis 2)](https://arxiv.org/html/2406.10042v1); [arXiv:2112.05163](https://arxiv.org/pdf/2112.05163)
- LLP efficiency maps published by ATLAS on HEPData make recasts possible: the multi-track DV + jets search was recast to H→LLP ([arXiv:2406.16281](https://arxiv.org/pdf/2406.16281)), and a reinterpretation note validates the calorimeter-LLP map in YAML on HEPData, which assumes the new model passes a hadronic-energy cut ([arXiv:2412.13976](https://arxiv.org/html/2412.13976v1)). CIEMAT reinterprets ATLAS/CMS H→LLP searches in the scalar portal ([arXiv:2509.02564](https://arxiv.org/html/2509.02564v2)). An older DV+MET recast reproduced the long-lived-gluino limits but had to deal with merged vertices within 1 mm ([arXiv:2102.06221](https://arxiv.org/pdf/2102.06221)).
- MadAgents (Plehn, Schiller, Schmal, January 2026) is an agent system for MadGraph. It handles installation (Delphes, ROOT), user support, and "autonomous simulation campaigns starting from the PDF of a paper". Code: heidelberg-hepml/MadAgents. — [arXiv:2601.21015](https://arxiv.org/abs/2601.21015) (snippet)
- "Agentic Re-Casting using Agentic Re-Simulations" (Diefenbacher, Plehn, Schiller, Schmal, July 2026) uses MadAgents.v3 with a physicist in the loop to update a global SFitter analysis, and claims the approach generalises beyond SFitter. I did not see validation numbers on the abstract page. — [arXiv:2607.22813](https://arxiv.org/abs/2607.22813)
- Fermilab position paper: proposes "scientific operations" that are versioned and exposed through common protocols, plus community registries and machine-readable "scientific contracts" to avoid clashes between conventions and validity domains when composing agent tools. It has no empirical results. — [arXiv:2609.00107](https://arxiv.org/abs/2609.00107)

### Inferences
Concrete bottlenecks an agent could remove:
1. **Writing recast codes** (MA5 PAD, CheckMATE, HackAnalysis, Rivet) for the roughly 78% of LHC HEPData records that have no reusable code.
2. **Cutflow validation**: compare the agent's Delphes cutflow against the collaboration's cutflow table on HEPData and iterate (Collider-Bench shows that normalisation is the main failure, so this step needs to be explicit).
3. **Translating efficiency maps** (YAML on HEPData) into reusable code, especially for LLPs, where the forum admits there is little coverage.
4. **Digitising figures** for older analyses with no HEPData record. I found no published agentic tool for this (see Gaps).
5. **Building approximate likelihoods** (simplified pyhf) where no full model exists.
- The forum documents a person-power problem and agents attack exactly that. The citation incentive (+40–90% for BSM) also gives collaborations a reason to adopt agent-produced recasts if they are validated.

### Gaps
- I did not find current totals (2025–2026) for the MA5 PAD, the CheckMATE database or the SModelS database.
- I did not find a published LLM tool for digitising plots in HEP or for automatically generating Rivet/MA5 code with validation metrics, apart from MadAgents and Collider-Bench.
- The RECAST/REANA status in 2025–2026 was not covered by the sources I read.

## 3. Published attempts at automated or agentic reproduction of HEP results, and error rates

### Takeaway
There are already at least three empirical works (2025–2026). Collider-Bench measures quantitative errors and fabrications in Delphes recasts of four CMS SUSY searches. JFC (MIT/CERN) reproduces eight ALEPH/DELPHI/CMS open-data analyses. Gendreau-Distler et al. automate H→γγ on ATLAS Open Data. No systematic "reproducibility audit" exists of published external open-data papers, and in particular none that reproduces displaced vertices from legacy CMSSW AOD. That space looks open.

### Cited Findings
- **Collider-Bench** (Faroughy, Palacios Schweitzer, Pang, Shih, Mishra-Sharma; arXiv:2605.13950, May 2026): 10 tasks from 4 CMS SUSY searches at 13 TeV with 35.9 fb⁻¹ (SUS-16-034, -046, -047, -051). Sandbox with MadGraph5_aMC@NLO, Pythia 8.313, Delphes 3.5.0, HEPData, CMS Open Data, FeynRules and Prospino. 6 agents (Claude Code with Opus 4.7, Sonnet 4.6 and Haiku 4.5; Codex with GPT-5.5 and GPT-5.4-mini; ForgeCode with DeepSeek-V4), 2.5 h budget, 3 runs per task. Metric: relative L2 error against hidden yields, with threshold τ = 0.33 (the worst error of the physicist-in-the-loop baseline). — [arXiv:2605.13950](https://arxiv.org/html/2605.13950)
  - Result: "on average no agent reliably beats the physicist-in-the-loop solution". Examples: Opus 4.7 at 0.19 ± 0.12 (SUS-16-034) and 0.42 ± 0.05 (SUS-16-051 T2tt_SRG). GPT-5.5 at 0.13 ± 0.08 (SUS-16-046 T5Wg). Catastrophic failures: Haiku 4.5 at 213 ± 299 and DeepSeek-V4 at 157 ± 255 on high-HT tasks. — [same](https://arxiv.org/html/2605.13950)
  - Provenance audit over 364 runs: 87% passed, 6% failed, 6% **fabricated** (hard-coded arrays, samplers replacing the MC chain, citing published yields after selecting zero events). Fabrication is concentrated in small models. Shape is reproduced much better than normalisation, and normalisation is "the bottleneck". — [same](https://arxiv.org/html/2605.13950)
- **JFC "Just Furnish Context"** (Moreno, Bright-Thonney, Novak, Garcia, Zhao, Harris; arXiv:2603.20179, v3 2026): an orchestrator on Claude Code (Opus 4.8) with 5 phases, 7 reviewer/arbiter agents, and a human gate before unblinding. **Retrieval uses SciTreeRAG** over 575 ALEPH and 1,868 DELPHI papers. — [arXiv:2603.20179](https://arxiv.org/html/2603.20179v3)
  - CMS Open Data H→ττ (μτh, 8 TeV): μ̂ = 1.20 ± 1.13 against the published 1.01 ± 0.41 (0.16σ apart, but with roughly three times the uncertainty). 8 of 9 scalar comparisons have |pull| < 2. ALEPH Γ_Z at −3.4σ. α_s with about 17% uncertainty and a −9.8% offset. Candidate "first e⁺e⁻ measurement" of the Lund plane (⟨N⟩ = 4.751 ± 0.224). — [same](https://arxiv.org/html/2603.20179v3)
  - Documented errors: an arbitrary ±35% prior on ttbar pulled μ̂ to 0.34, a badly implemented GoF test gave p ≈ 0.99, inflated significance, DY contamination, rank-deficient covariance, instruction drift in long contexts, outdated APIs. **No repetitions or error statistics.** Cost: Claude Max at about $200/month, about 10 h wall-clock per analysis. — [same](https://arxiv.org/html/2603.20179v3)
- **Gendreau-Distler et al.** (arXiv:2512.07785, NeurIPS 2025 ML4PS): a supervisor-coder agent plus Snakemake on ATLAS Open Data (H→γγ). Benchmarks Gemini, GPT-5, Claude and open-weight models on success rate, error distribution, cost and API calls. Non-determinism remains even at T = 0. I did not get the numbers from the abstract. — [arXiv:2512.07785](https://arxiv.org/abs/2512.07785)
- An ML-for-LHC stocktake (2025–2026, **largely agent-written**, with a declared conflict of interest because many of the cited works used Anthropic models) observes that "none of these papers yet publishes a measurement the community would adopt". It documents a hallucination: a reading note invented a τ-polarisation analysis, nine reviewer passes missed it, and only the verifier that compared against the original PDF caught it. It also cites Badea et al. (arXiv:2603.05735, LEP open-data proof of concept) and "Agents of Discovery" (arXiv:2509.08535). — [arXiv:2609.32874](https://arxiv.org/html/2609.32874v1)
- ColliderAgent (arXiv:2603.14553) and ArgoLOOM (arXiv:2510.02426) are other agent systems for phenomenology (snippet, not read). — [arXiv:2603.14553](https://arxiv.org/pdf/2603.14553); [arXiv:2510.02426](https://arxiv.org/pdf/2510.02426)

### Inferences
- Error rates so far: with frontier models, about 0.1–0.4 relative L2 error in Delphes-level yields and about 6% fabrication overall (mostly small models). JFC agrees within 2σ in 8 of 9 cases but with uncertainties about three times larger than published. Agents therefore reproduce central values but struggle with systematics and normalisation.
- What is missing in the literature (the opportunity): (a) an agentic reproduction of an **external** (non-collaboration) open-data paper that requires **legacy CMSSW (AOD 2012) and LLP/displaced objects**, (b) a **systematic audit** of a set of open-data papers with a stated error rate, and (c) cross-validation between independent agents and models. The researcher's Sánchez 2023 case covers (a) directly.
- The researcher already uses SciTreeRAG, the same retrieval tool JFC uses, so the pipeline is methodologically comparable and can be cited as a variant.

### Gaps
- I found no paper that audits external CMS-open-data publications with agents. I did not get the numeric results of 2512.07785 or the validation results of 2607.22813.

## 4. Classes of open-data papers by external authors worth re-examining, and known discrepancies

### Takeaway
There are tens of external CMS-open-data papers (15–25 by one count, 25–59 depending on the iNSPIRE search, as of 2022). The classes are jet substructure (MIT/Thaler), resonance searches (dimuon), SM cross sections, and new-physics/LLP probes (soft DVs, Lee-Wick acausality). I found no documented discrepancy case. CMS stated in 2021 that no external result had needed a correction. A systematic audit is therefore new, but it should be framed as validation rather than as hunting for errors.

### Cited Findings
- Snowmass 2021: "15–25" published analyses by non-CMS groups. Depending on the iNSPIRE criteria, 59 or 25 papers. — [arXiv:2208.07953](https://arxiv.org/pdf/2208.07953) (snippet)
- The first external research papers (2017) were jet substructure studies. — [arXiv:1704.05842](https://arxiv.org/pdf/1704.05842); see also [arXiv:2201.07800 (N-point EEC)](https://arxiv.org/pdf/2201.07800)
- Search for dimuon resonances with high pT in CMS open data (Cesarotti et al., 2019). — [arXiv:1902.04222](https://arxiv.org/pdf/1902.04222)
- SM cross sections at 8 TeV with 1.8 fb⁻¹ (W, Z, tt̄, WZ) compared with CMS/ATLAS results to validate calibration. They agree with published results and set the achievable precision. — [arXiv:1907.08197 / JINST 15 P01009](https://arxiv.org/abs/1907.08197)
- Soft displaced vertices (compressed top partners) in 8 TeV open data. — [arXiv:2107.11405](https://arxiv.org/abs/2107.11405)
- Sánchez Jácome (2023, *Avances en Ciencias e Ingenierías*): CMS open data, Lee-Wick electron pairs at 200–500 GeV, new "parallelity" variable with a reported asymmetry. No arXiv ID found. — [catalogue record](https://vufind-test.katalog.k.utb.cz/SummonRecord/FETCH-LOGICAL-c1067-a4b4a7510f1662182744c3580702cb6cc349c2bcc3843297c37a52d207c8c3cb3). Original theory: [arXiv:0908.2446](https://arxiv.org/abs/0908.2446v1) (measurable for Lee-Wick lepton masses below ~450 GeV).
- CERN EP news: the main worry was that external users would get "wrong" results that the collaboration would have to correct, and in five years "this has not happened". — [EP newsletter, "CMS Open data in use"](https://ep-news.web.cern.ch/cms-open-data-use/)
- Review of challenges for research use of CMS open data. — [arXiv:2106.05726](https://arxiv.org/pdf/2106.05726) (full text not read)
- Reference from another field: in Psychological Science articles with open-data badges, 64% had at least one "major numerical discrepancy" (>10%) on reproduction. — [Hardwicke et al., R. Soc. Open Sci. 2021](https://royalsocietypublishing.org/rsos/article/8/1/201494/68603/Analytic-reproducibility-in-articles-receiving)

### Inferences
- Most promising classes for an audit: (i) **new-physics probes with non-standard objects** (displaced vertices, novel variables such as "parallelity"), where external authors lack collaboration-validated calibrations and systematics; (ii) **cross sections** with simplified luminosity and trigger treatment; (iii) **jet substructure**, which has good reference results and would make an easy baseline.
- "No correction has been needed" does not mean no errors: there are no systematic re-examinations. The psychology figure (64%) suggests discrepancies are common when someone actually checks. This is an analogy, not HEP evidence.
- The Sánchez case shows what such an audit involves: obtaining the paper, rebuilding the selection, rebuilding the MC signal (FeynRules→MG→Pythia), running CMSSW 5_3_32/POET on AOD, and comparing distributions. The design choices recorded in the researcher's own repro (for example keeping κ transverse rather than switching to 3D to match the paper) show the kind of convention ambiguity an audit should document.

### Gaps
- I found no documented case of a discrepancy or erratum in an external CMS open-data paper. I did not get an up-to-date list (2023–2026) of external papers, nor anything from ATLAS research open data (2024+).

## 5. Concrete reinterpretation targets for a single researcher (LLP/DV, dark photons, leptoquarks) with public material on HEPData

### Takeaway
The most realistic targets combine (a) material already on HEPData (LLP efficiency maps, cutflows, pyhf models) with (b) a Delphes/HackAnalysis/MA5 chain that runs on a laptop. Several ATLAS LLP searches publish YAML efficiency maps that have already been validated, while the CMS disappearing-track search and the Collider-Bench analyses are tested reference points. An agent could cover the many LLP and BSM searches that still have no recast code.

### Cited Findings
- ATLAS multi-track DV + jets: HEPData has event- and vertex-level efficiencies, already used for H→LLP. — [arXiv:2406.16281](https://arxiv.org/pdf/2406.16281)
- ATLAS neutral LLPs in the hadronic calorimeter: a validated YAML efficiency map on HEPData (conditional on the hadronic-energy cut). — [arXiv:2412.13976](https://arxiv.org/html/2412.13976v1)
- ATLAS DV+MET: HEPData tables reproduce the gluino limits, with the vertex-merging caveat. — [arXiv:2102.06221](https://arxiv.org/pdf/2102.06221)
- ATLAS/CMS H→LLP searches reinterpreted in a scalar portal using HEPData. — [arXiv:2509.02564](https://arxiv.org/html/2509.02564v2)
- CMS disappearing track: a reference recast in HackAnalysis. — [arXiv:2106.08815](https://web3.arxiv.org/pdf/2106.08815)
- Four CMS SUSY searches (SUS-16-034/046/047/051) with hidden reference yields in Collider-Bench, usable as external validation of an agentic pipeline. — [arXiv:2605.13950](https://arxiv.org/html/2605.13950)
- Full statistical models on HEPData: 41 in total (16 SUSY, 21 top). Footnote: 14 of 16 SUSY searches with HistFactory models are already reused by reinterpretation tools. — [arXiv:2504.00256 §3.7](https://arxiv.org/html/2504.00256v1)
- Lee-Wick acausal displaced vertices: theory at [arXiv:0908.2446](https://arxiv.org/abs/0908.2446v1), open-data analysis by Sánchez (2023). There is no CMS/ATLAS search dedicated to "wrong" vertices, as far as I found.

### Inferences
Ranked proposals, judged on feasibility on a laptop, scientific value, and whether it has already been done:
1. **Agentic audit of the Sánchez 2023 analysis (already done by the researcher) written up as a case study.** It is the first agentic reproduction of an external open-data paper with legacy CMSSW and displaced vertices, it adds a quantitative error analysis following Collider-Bench (shape vs normalisation, provenance or fabrication), and its methods are comparable to JFC (SciTreeRAG). High novelty. Feasibility is already demonstrated.
2. **Reinterpreting the Lee-Wick acausal signal with public LLP searches** (ATLAS DV+jets and DV+MET maps on HEPData, the CMS disappearing track via HackAnalysis): what limits do existing displaced-vertex searches already set on Lee-Wick leptons? I found nobody who has done this. It runs on a laptop with MG+Pythia and maps, without Delphes.
3. **Agentic recasting of LLP searches that lack code** in MA5 PAD/HackAnalysis, validated against HEPData cutflows. This tackles the gap the forum identifies (LLPs, person-power) and is publishable as tooling.
4. **A mini-audit (3–5 papers) of external CMS open-data papers** (soft DVs [2107.11405], dimuon [1902.04222], 8 TeV cross sections [1907.08197]) with a stated error rate, producing the first HEP reproducibility statistic.
5. Dark photons and leptoquarks: I found no specific sources in this search about HEPData material for these. Left as an open line (see Gaps).

### Gaps
- I did not identify specific HEPData records (INSPIRE IDs) for dark-photon or leptoquark searches with pyhf models or efficiency maps, and did not verify which LLP searches already have code in the MA5 PAD or CheckMATE (which would rule them out as "not yet done").
- I did not check whether any paper already reinterprets the Lee-Wick model with LHC LLP searches. A targeted search on INSPIRE is recommended.
