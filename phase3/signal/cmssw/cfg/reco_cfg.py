# Step 2: RAW2DIGI,L1Reco,RECO -> AODSIM (record 12052 recipe without VALIDATION/DQM)
import sys, os
sys.path.insert(0, '/work/cmssw/cfg')
from common import *
execfile('/work/cmssw/driver/raw_reco.py')
process.source.fileNames = cms.untracked.vstring('file:' + P['IN'])
conditions(process)
set_seeds(process, P['SEED'] + 2)
common_io(process, 'AODSIMoutput')
# extra (non-standard AODSIM) truth for vertex studies: Geant4 SimTracks/SimVertices
process.AODSIMoutput.outputCommands += ['keep SimTracks_g4SimHits_*_*', 'keep SimVertexs_g4SimHits_*_*']
