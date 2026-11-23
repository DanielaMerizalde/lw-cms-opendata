# Step 0: HepMC2 (MCFileSource) -> VtxSmeared (Realistic8TeVCollision) -> genParticles/genJets -> SimG4 (GEN-SIM)
# Base: cmsDriver ZEE_8TeV_cfi.py ... --step GEN,SIM --beamspot Realistic8TeVCollision (open-data record 12052 recipe);
# the placeholder Pythia6 generator is removed and replaced by LWMCFileSource (stock MCFileSource flags events as real data, which PoolSource/setRunNumber and the MC-specific steps reject).
import sys
sys.path.insert(0, '/work/cmssw/cfg')
from common import *
execfile('/work/cmssw/driver/raw_gensim.py')
process.source = cms.Source("LWMCFileSource",  # = MCFileSource but isRealData()=False (cmssw/build_plugin.sh)
    fileNames = cms.untracked.vstring('file:' + P['IN']),
    firstRun = cms.untracked.uint32(1),
    firstEvent = cms.untracked.uint32(P['FIRST']))
del process.generator
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.schedule = cms.Schedule(process.generation_step, process.simulation_step, process.endjob_step, process.RAWSIMoutput_step)
# MCFileSource puts the HepMCProduct under the label 'source' (not 'generator'): rewire its consumers.
# VtxSmeared shifts the HepMC event in place (BaseEvtVtxGenerator::applyVtxGen), so genParticles and Geant4
# see the smeared vertices.
process.VtxSmeared.src = cms.InputTag('source')
process.genParticles.src = cms.InputTag('source')
process.g4SimHits.Generator.HepMCProductLabel = cms.string('source')
conditions(process)
set_seeds(process, P['SEED'])
common_io(process, 'RAWSIMoutput')
