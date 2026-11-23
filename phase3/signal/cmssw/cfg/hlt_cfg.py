# Step 1: DIGI,L1,DIGI2RAW,HLT:7E33v2 (+ optional 2012_Summer_50ns_PoissonOOTPU pile-up), GEN-SIM-RAW
# Base: cmsDriver step1 ... (record 12052 recipe). LW_PU=1 -> with PU (MinBias file of the recipe, LW_PUFILE overrides it)
import sys, os
sys.path.insert(0, '/work/cmssw/cfg')
from common import *
PU = os.environ.get('LW_PU', '1') == '1'
execfile('/work/cmssw/driver/raw_hlt_pu.py' if PU else '/work/cmssw/driver/raw_hlt_nopu.py')
process.source.fileNames = cms.untracked.vstring('file:' + P['IN'])
# PU input: the recipe streams the MinBias file by xrootd; on this host that made the HLT step ~85% I/O wait
# (155-174 s wall vs 23-26 s CPU per event), so a byte-identical local copy (pu/fetch_pu.sh) is used when present.
LOCALPU = '/work/pu/MinBias_FEF2F4CC.root'
if PU and os.environ.get('LW_PUFILE'):
    process.mix.input.fileNames = cms.untracked.vstring(os.environ['LW_PUFILE'].split(','))
elif PU and os.path.exists(LOCALPU):
    process.mix.input.fileNames = cms.untracked.vstring('file:' + LOCALPU)
if PU:
    print 'LW: PU input', list(process.mix.input.fileNames)
# Run2012_AB_C_D_oneRunPerEra: ThrowAndSetRandomRun draws the run with random.SystemRandom (not seedable), which would
# give different runs (conditions, PU profile) to the causal and acausal job of the same chunk. Replace it by the same
# weighted draw with a generator seeded by the chunk seed -> identical run for causal/acausal, reproducible.
if hasattr(process.source, 'setRunNumber'):
    import random
    runs = [(194533, 5.3), (200519, 7.0), (206859, 7.3)]
    u = random.Random(P['SEED'] + 7).uniform(0, sum(w for r, w in runs))
    acc = 0.
    for r, w in runs:
        acc += w
        if acc >= u:
            break
    process.source.setRunNumber = cms.untracked.uint32(r)
    print 'LW: setting runNumber (deterministic) to', r
conditions(process)
set_seeds(process, P['SEED'] + 1)
common_io(process, 'RAWSIMoutput')
