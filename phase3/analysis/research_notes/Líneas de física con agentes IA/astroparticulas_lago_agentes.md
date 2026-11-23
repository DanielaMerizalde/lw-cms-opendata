# Astroparticle physics with WCDs / LAGO where LLM agents could run the simulation-analysis chain (public data + laptop)

Research date: 2026-11-17. About 15 search/fetch calls. Mostly abstracts, arXiv/PoS landing pages and project pages; full texts were not read except where stated.

## 1. What public datasets and tools exist, and what fits on a laptop?

### Takeaway
The simulation side is open: ARTI (BSD-3: CORSIKA + Magnetocosmics + Geant4 WCD model) is on GitHub. The data side is mixed. Auger Open Data (10% of cosmic-ray events plus 100% of atmospheric and space-weather scaler data, with a larger 30% release announced), the IceCube 10-year point-source sample, HAWC Crab event lists and NMDB neutron-monitor data are all public and small enough for a laptop. I found no explicit public data-release policy for LAGO WCD data itself.

### Cited Findings
- **ARTI** simulates the signals that air-shower secondaries produce in a detector at any site (latitude, longitude, altitude), taking atmospheric, geomagnetic and detector conditions into account. It also gives expected GRB and steady-source fluxes and muon fluxes for muography. Components: Magnetocosmics v2.0, CORSIKA v7.7402 (QGSJETII-04 + GHEISHA 2002d, non-flat geometry), Geant4 4.10.03.p03 with a configurable WCD model in `wcd/`, and ROOT 6.20.08. License BSD-3. Linux only (Windows users need a VM). — [ARTI GitHub](https://github.com/lagoproject/arti)
- ARTI takes predefined site characteristics from the LAGO Data Management Plan and stores the user's ORCID in output metadata. The GitHub page links Zenodo and the main paper (DOI 10.1140/epjc/s10052-022-10883-z), and a cloud version (oneDataSim) is on the EOSC Marketplace. A pre-compiled production CORSIKA is available "on request". The page states no LAGO data-sharing policy. — [ARTI GitHub](https://github.com/lagoproject/arti)
- The EOSC-Synergy paper says LAGO data must be "transferred, analyzed, catalogued, preserved, and provided for internal and public access and data-mining" in an open e-science environment, and presents ARTI as the first LAGO framework following FAIR principles. — [arXiv:2111.11190](https://arxiv.org/abs/2111.11190)
- **Auger Open Data portal** (launched Feb 2021): 10% of cosmic-ray data from 2004–2018 and 100% of atmospheric and space-weather data. — [Auger news](https://www.auger.org/news/scientific-highlights/343-the-pierre-auger-observatory-open-data); described in EPJC (Jan 2025) — [EPJC](https://epjc.epj.org/articles/epjc/abs/2025/01/10052_2024_Article_13560/10052_2024_Article_13560.html). Policy PDF: [opendata.auger.org](https://opendata.auger.org/AugerOpenDataPolicy.pdf)
- The portal already holds more than 80,000 events above 10^17 eV (SD and FD), from calibrated traces up to high-level reconstruction, plus low-energy particle counting rates for space weather. The ICRC 2025 contribution announces a release of 30% of SD events above 2.5×10^18 eV from 2004–2022 (about 24,000 km² sr yr), plus the FD events used for energy calibration. No release date is given. — [arXiv:2507.08504](https://arxiv.org/abs/2507.08504); [PoS ICRC2025 501/1251](https://pos.sissa.it/501/1251)
- **IceCube**: 10-year all-sky point-source track sample (Apr 2008–Jul 2018) with binned instrument response functions. It is hosted on Harvard Dataverse and as the HEASARC table ICECUBEPSC. It cannot be combined with other IceCube releases and is not meant for diffuse-spectrum analyses. — [arXiv:2101.09836](https://arxiv.org/abs/2101.09836v1); [IceCube data page](https://icecube.wisc.edu/science/data/PS-IC40-IC86_VII); [HEASARC](https://heasarc.gsfc.nasa.gov/W3Browse/icecube/icecubepsc.html)
- **HAWC**: Crab Nebula event lists were made public alongside a 2022 paper that made HAWC data Gammapy-compatible. — [arXiv:2203.05937](https://arxiv.org/pdf/2203.05937). A 10-year HAWC science review: [arXiv:2512.03938](https://arxiv.org/pdf/2512.03938)
- **NMDB**: real-time and historical data from more than 50 neutron monitors worldwide, distributed as official PI-provided data, with acknowledgement requested. — [nmdb.eu](https://nmdb.eu/); [Kiel-UP 2021](https://macau.uni-kiel.de/servlets/MCRFileNodeServlet/macau_derivate_00002376/kiel-up_%202748-3150_p17.pdf)

### Inferences
- A laptop can handle: Auger scaler and atmospheric time series, NMDB time series, the IceCube PS sample (about 1 million events), HAWC Crab event lists in Gammapy, and ARTI/CORSIKA runs at low energies (GeV–TeV secondaries per site and hour of flux). CORSIKA above roughly 10^17 eV needs thinning or CONEX to stay laptop-sized.
- The researcher's LAGO membership is the realistic route to LAGO WCD data. Outsiders would need to work with Auger/NMDB plus ARTI simulations.

### Gaps
- No official LAGO public-data portal or release policy was found. The ARTI page mentions only a "Data Management Plan", without a URL.
- HAWC has no general public-data portal that I could confirm beyond the Crab event lists.
- The Meiga framework (Geant4 for WCDs / muography) is not on the ARTI page. Its repository and licence were not verified.

## 2. Open physics questions 2023–2026 that are reachable

### Takeaway
Space weather with WCDs (Forbush decreases during the solar-cycle-25 maximum: May 2024, Jan 2026) is the most accessible and most LAGO-native topic. The muon puzzle and LIV-in-air-showers are active topics, reachable with CORSIKA/CONEX on modest compute. LIV is the natural link to the researcher's Lee-Wick/acausality work.

### Cited Findings: space weather / Forbush decreases
- LAGO WCD "Tanca" (UNICAMP, 11,400 L, 3 PMTs, inside the South Atlantic Anomaly) saw the 20 Jan 2026 Forbush decrease (fast ICME, G4 storm) with an 8.88% peak suppression. That is smaller than in neutron monitors because the WCD signal is muon-dominated, with an effective primary threshold of about 30–40 GeV. The authors argue that WCDs extend the energy coverage of ground monitoring. Presented as a poster at Space Climate 10, June 2026; not an arXiv paper. — [Indico SC10](https://indico.global/event/17578/contributions/152370/)
- LAGO "Neurus" WCD at the Marambio Antarctic station (installed 2019): counting-mode WCDs are highly sensitive to Forbush decreases. — [arXiv:2302.00322](https://pdf.arxiv.org/pdf/2302.00322); AASWO talk: [IceCube events PDF](https://events.icecube.wisc.edu/event/266/contributions/11188/attachments/8477/11256/Work%20and%20Recent%20Developments%20of%20AASWO%20%28Argentinean%20Antarctic%20Space%20Weather%20Observatory%29.pptx.pdf)
- The 10 May 2024 Forbush decrease was observed by the ALPAQUITA air-shower array in the 70–1000 GV rigidity range. — [arXiv:2601.08154](https://arxiv.org/pdf/2601.08154)
- An anisotropic Forbush decrease on 24 March 2024 was analysed with the neutron-monitor network (ICRC 2025). — [PoS 501/1333](https://pos.sissa.it/501/1333)
- LAGO lists space weather and climate monitoring among its science goals: small WCDs with adapted analysis can see space-weather phenomena on several time scales. — [arXiv:2111.11190](https://arxiv.org/abs/2111.11190)

### Cited Findings: muon puzzle
- Simulations with state-of-the-art hadronic models show a muon deficit relative to data. Review: [arXiv:2105.06148](https://arxiv.org/abs/2105.06148). The WHISP 8-experiment meta-analysis finds a muon excess above about 10 PeV even with post-LHC models. — [arXiv:2001.07508](https://arxiv.org/pdf/2001.07508)
- A 2024 WHISP update combining 10 experiments says the observed puzzle may depend on experimental conditions. — [Indico ICHEP/2024 contribution](https://indico.global/event/7282/contributions/67855)
- EPOS.LHC-R (Pierog & Werner, ICRC 2025) is presented as a global approach toward resolving the puzzle. — via [KIT publication](https://publikationen.bibliothek.kit.edu/1000189828/173669146) (snippet-level; not read in full)

### Cited Findings: Lorentz-invariance violation (link to acausality / Lee-Wick)
- Auger LIV limits from spectrum, composition and photon searches (5σ): δhad,0 < 10⁻¹⁹, δhad,1 < 10⁻³⁸ eV⁻¹, δhad,2 < 10⁻⁵⁷ eV⁻². The bounds depend strongly on composition at the highest energies. — [arXiv:2112.06773](https://arxiv.org/abs/2112.06773)
- With LIV, neutral pions above a threshold energy stop decaying and start interacting. That gives more muons, smaller muon fluctuations, a shallower Xmax and less deposited energy (so the primary energy is underestimated). — [arXiv:2501.19322](https://arxiv.org/pdf/2501.19322) (UHECR2024 BSM review); [PoS ICRC2021 395/340](https://pos.sissa.it/395/340) (Auger, Trimarelli et al.)
- Dissenting view: a 2024 preprint argues that tiny LIV could instead suppress the electron number and leave muons unchanged, offered as an explanation of the muon excess. — [arXiv:2412.08349](https://arxiv.org/html/2412.08349v1)
- Other recent LIV/cosmic-ray work: [arXiv:2503.03124](https://arxiv.org/pdf/2503.03124) (two-sided proton LIV constraints, 2025, contents not verified); [arXiv:2503.07867](https://web3.arxiv.org/pdf/2503.07867) (Aloisio, UHECR2024); [arXiv:2404.15838](https://www.arxiv.org/pdf/2404.15838) (post-GZK events as an LIV signal, EPJC 2024)

### Cited Findings: detector-response modelling for WCDs
- LAGO has a full Geant4 WCD simulation (Bucaramanga) that reproduces the vertical-muon pulse shape. — [arXiv:1503.07270](https://arxiv.org/pdf/1503.07270)
- ARTI+Meiga training data (one day at LAGO Bariloche) with OPTICS density clustering identifies the origin particle of a single WCD pulse with high confidence. — Torres Peralta et al., *Atmosphere* 2024, doi:10.3390/atmos15091039 (via [search record](https://harvester.ues.edu.sv/vufind/ProQuestFSGRecord/3110395805/Details)). LAGO-INDICA 2025 slides show cluster probabilities of about 0.97 for muons versus about 0.016 for e± (preliminary). — [slides](https://jupyterhd.redclara.net/event/245/sessions/91/attachments/384/624/LAGO-INDICA%202025.pdf)
- ML muon tagging in small 4-PMT WCDs (Geant4 + CORSIKA) works well. — [arXiv:2101.11924](https://arxiv.org/pdf/2101.11924v1.pdf); SWGO-oriented gamma/hadron work using muons: [arXiv:2101.10109](https://arxiv.org/pdf/2101.10109v1)
- 2025 Geant4 characterisation of μ, e, γ and hadron signals (energy deposit, PMT charge) in a WCD (preprint). — [Preprints.org 202510.0537](https://www.preprints.org/manuscript/202510.0537/download/final_file)

### Inferences
- **Strongest near-term WCD topic:** multi-site Forbush-decrease energy dependence for the solar-cycle-25 maximum events (May 2024, Oct 2024, Jan 2026), done as LAGO WCD vs NMDB vs Auger scalers. ARTI gives each site's effective primary-rigidity response, and the fit extracts the rigidity spectrum of the decrease. The Tanca abstract already shows the WCD threshold (about 30–40 GeV) is complementary to neutron monitors, and nobody seems to have published a combined multi-site spectral analysis.
- **Muon puzzle / LIV:** an air-shower LIV paper with π⁰ suppression implemented in CORSIKA/CONEX is mostly simulation work, and so suits an agent. It links to the researcher's acausality interest, since LIV and Lee-Wick acausality are both modified-dispersion or modified-propagator effects (conceptual link, not sourced). Full Auger muon data are not public, so tests would rely on published WHISP z-values and on Auger Open Data reconstructed parameters.
- GRBs with ground arrays (LAGO's original single-particle technique) and anisotropy were not researched in depth here.

### Gaps
- No 2024–2026 LAGO arXiv paper on Forbush decreases was found. Whether a multi-site LAGO FD analysis is already under way inside the collaboration is unknown.
- No dedicated 2024–2026 muon-puzzle review was found. The WHISP 2024 update is only a conference talk.
- No 2024–2026 Auger LIV limit paper was found that supersedes arXiv:2112.06773.
- Cosmic-ray anisotropy, solar modulation (long-term) and GRB ground searches: no sources were collected in this pass.

## 3. Work using ML or LLM agents to run CORSIKA/Geant4 or analyse cosmic-ray data

### Takeaway
Agentic CORSIKA already exists. CorsikaAgent (arXiv:2610.16607, Oct 2026) configures, runs and validates air-shower simulations with full provenance, and extends them to Mars and Venus. GRACE (Geant4 experiment design) and PHITSBench (radiation-transport input generation) give the benchmarking context. I found nothing that agentically chains ARTI-style flux → Geant4 WCD response → comparison with real WCD/NMDB data. That gap is the opening.

### Cited Findings
- **CorsikaAgent** (Chen, Zhao, Shen, Gao, Liu, Li, Wang, Li; submitted 12 Oct 2026, hep-ph) is an "auditable" LLM system for configuring, executing and validating air-shower simulations. It records each steering card, executable, seed, log and analysis script, and can reconfigure atmosphere, magnetic field and electric field. It uses CORSIKA (including CORSIKA 8), UrQMD, and Sibyll 2.3e or QGSJET-III. Results: sea-level muon spectra at 0° and 75° that agree with data and parametrisations; an independent sampling strategy chosen by the agent that reproduces them; the Mars CORSIKA 8 benchmark reproduced; a first prediction of the Venus surface muon flux. Limitations: proton-only primaries, limited high-momentum statistics, incomplete systematics. No ARTI or LAGO involvement is stated. — [arXiv:2610.16607](https://arxiv.org/abs/2610.16607)
- **GRACE**: an LLM agent that turns a prompt or paper into a runnable toy simulation for HEP/NP experiment design. It escalates from parametric models to full Geant4 runs under a budget and tracks provenance; it supports Claude, GPT and local models. — [arXiv:2602.15039](https://arxiv.org/abs/2602.15039)
- **PHITSBench** (Ji & Boriskina, Jul 2026): 282 tasks. Zero-shot GPT-5.4 scored 95% on Edit, 70% on Repair and 0% on full Reproduce. A machine-readable knowledge catalog raised Reproduce to 57%, and agentic workflows to 66–73%. The remaining failures are wrong choices of physical observables, not syntax. — [arXiv:2607.09789](https://arxiv.org/abs/2607.09789)
- Classical ML on WCD data: OPTICS clustering of LAGO pulses (Torres Peralta et al. 2024) and ML muon tagging ([arXiv:2101.11924](https://arxiv.org/pdf/2101.11924v1.pdf), [arXiv:2101.10109](https://arxiv.org/pdf/2101.10109v1)); see section 2.

### Inferences
- PHITSBench suggests where agents add value: execution-grounded loops in which the agent edits, runs and checks against reference observables. They fail at choosing the physics observable, so the researcher's role is defining the observables and validation targets. A "machine-readable knowledge catalog" for ARTI/CORSIKA steering, comparable to the PHITS one, could itself be a publishable contribution (an ARTI/WCD benchmark).
- CorsikaAgent does not cover detector response (Geant4 WCD), geomagnetic cutoffs (Magnetocosmics) or comparison with ground monitor data. That is exactly ARTI's chain, so "an ARTI agent for WCD space weather" would not duplicate it.

### Gaps
- No LLM-agent work specific to LAGO, Auger open data or NMDB analysis was found.
- CorsikaAgent's affiliations and code availability were not verified.

## 4. Which would make a strong single-author or small-team paper within months, and who could host it?

### Takeaway
Ranked by feasibility: (1) a multi-site, energy-resolved Forbush-decrease study (cycle-25 events) combining LAGO WCD, NMDB and Auger scalers, with ARTI-computed rigidity responses run by an auditable agent; (2) an agentic ARTI/Geant4 WCD-response benchmark or validation paper, extending the researcher's noise/response work; (3) a CORSIKA/CONEX study of LIV π⁰-decay suppression versus the muon excess, linked to acausality themes. Natural hosts are the LAGO collaboration groups (UNICAMP/Brazil, Bariloche/Argentina CAB-CNEA, Bucaramanga/UIS Colombia, Marambio/Antarctic AASWO) and Auger groups for open-data work.

### Cited Findings
- Groups active in LAGO WCD space weather: UNICAMP (Fauth, dos Santos) with Bayreuth (Kuhn), Tanca detector — [Indico SC10](https://indico.global/event/17578/contributions/152370/); Marambio/Antarctic (AASWO, Argentina) — [arXiv:2302.00322](https://pdf.arxiv.org/pdf/2302.00322)
- LAGO Bariloche site and ARTI+Meiga ML pipeline (Torres Peralta et al.) — [search record](https://harvester.ues.edu.sv/vufind/ProQuestFSGRecord/3110395805/Details); [LAGO-INDICA 2025 slides](https://jupyterhd.redclara.net/event/245/sessions/91/attachments/384/624/LAGO-INDICA%202025.pdf)
- Bucaramanga (Colombia) Geant4 WCD simulation group — [arXiv:1503.07270](https://arxiv.org/pdf/1503.07270)
- EOSC-Synergy / CIEMAT (Rubio-Montero) cloud and FAIR infrastructure for ARTI — [arXiv:2111.11190](https://arxiv.org/abs/2111.11190)
- Auger open data explicitly supports space-weather studies through 100% of the scaler and atmospheric data. — [Auger news](https://www.auger.org/news/scientific-highlights/343-the-pierre-auger-observatory-open-data)

### Inferences
- **Option 1 (months, highest chance of acceptance):** needs LAGO WCD rates (internal access through the collaboration), NMDB and the Auger scaler release. ARTI runs per site for the cutoff and response, so the yield function is pure simulation and runs on a laptop at GeV energies. The agent's role: reproducible ARTI runs per site and date, automated FD detection, baseline fitting and pressure/temperature correction, and spectral fits. Target journals: Space Weather, JGR Space Physics, Astroparticle Physics.
- **Option 2:** builds directly on the researcher's first-author WCD noise/response paper. Its novelty is execution-grounded agent validation of WCD simulation, with a PHITSBench-style metric applied to ARTI/Geant4. Suits a small team (with an ARTI/Meiga developer).
- **Option 3:** riskier on physics. Implementing LIV in CORSIKA's decay tables is feasible, but competes with the Auger internal analysis (Trimarelli et al.). The angle is the Lee-Wick-motivated modified π⁰ propagator versus generic LIV, and it can be done alone with CONEX on a laptop.
- An Auger open-data-only paper (for example, scaler-based Forbush catalogue for cycle 24/25 with NMDB comparison) avoids any collaboration dependency, but Auger's open-data policy terms must be checked (policy PDF linked above).

### Gaps
- LAGO's internal publication policy (whether a single-author paper using collaboration WCD data is allowed) was not found.
- Whether the Auger open scaler data extend into the 2024–2026 events (the 2021 release covers up to 2018 for CR events; scaler coverage dates not verified).
- No funding or hosting calls (for example, LAGO/RedCLARA, EOSC) were researched.
