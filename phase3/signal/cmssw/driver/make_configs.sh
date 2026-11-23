#!/bin/bash
# Run inside cmsopendata/cmssw_5_3_32 (entrypoint sets up CMSSW). Writes raw cmsDriver configs into /work/cmssw/driver/
# Recipe: CERN Open Data record 12052 (EventProductionExamplesTool, branch 2012, MCQCDProductionMLTrackInfo).
set -e
cd /work/cmssw/driver
# step0 GEN-SIM (generator fragment is a placeholder: replaced by MCFileSource in the patch step)
cmsDriver.py ZEE_8TeV_cfi.py --fileout file:gensim.root --mc --eventcontent RAWSIM \
  --customise Configuration/StandardSequences/SimWithCastor_cff.customise,Configuration/DataProcessing/Utils.addMonitoring \
  --beamspot Realistic8TeVCollision --datatier GEN-SIM --conditions=START53_V27::All --step GEN,SIM \
  --datamix NODATAMIXER --python_filename raw_gensim.py --no_exec -n 10
# step1 DIGI,L1,DIGI2RAW,HLT:7E33v2 with 2012 Summer 50ns PU (recipe MinBias file, CERN open data EOS)
cmsDriver.py step1 --filein file:gensim.root --fileout file:hlt.root --mc --eventcontent RAWSIM \
  --runsScenarioForMC Run2012_AB_C_D_oneRunPerEra --datatier GEN-SIM-RAW --conditions=START53_V27::All \
  --step DIGI,L1,DIGI2RAW,HLT:7E33v2 --python_filename raw_hlt_pu.py --no_exec \
  --customise Configuration/DataProcessing/Utils.addMonitoring -n 10 \
  --pileup_input root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2012/Summer12/MinBias_TuneZ2star_8TeV-pythia6/GEN-SIM/START50_V13-v3/0002/FEF2F4CC-0E6A-E111-96F6-0030487F1C57.root \
  --pileup 2012_Summer_50ns_PoissonOOTPU
# same without PU (fallback / comparison)
cmsDriver.py step1 --filein file:gensim.root --fileout file:hlt.root --mc --eventcontent RAWSIM \
  --runsScenarioForMC Run2012_AB_C_D_oneRunPerEra --datatier GEN-SIM-RAW --conditions=START53_V27::All \
  --step DIGI,L1,DIGI2RAW,HLT:7E33v2 --python_filename raw_hlt_nopu.py --no_exec \
  --customise Configuration/DataProcessing/Utils.addMonitoring -n 10
# step2 RAW2DIGI,L1Reco,RECO -> AODSIM (recipe also runs VALIDATION/DQM; dropped: not needed)
cmsDriver.py step2 --filein file:hlt.root --step RAW2DIGI,L1Reco,RECO --datatier AODSIM \
  --conditions START53_V27::All --fileout file:aodsim.root --mc --eventcontent AODSIM \
  --python_filename raw_reco.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 10
ls -la
