import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import FWCore.PythonUtilities.LumiList as LumiList
opts = VarParsing.VarParsing('analysis')
opts.register('fileList', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, '')
opts.register('out', 'wdv3.root', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, '')
opts.register('isData', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, '')
opts.register('json', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, '')
opts.register('final', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, 'v3 final: only cleaning 0 + AVF')
opts.parseArguments()
isData = bool(opts.isData)
process = cms.Process('WDV3')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(opts.maxEvents))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))
files = [l.strip() for l in open(opts.fileList) if l.strip()]
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(*files),
    inputCommands=cms.untracked.vstring(
        'drop *', 'keep *_TriggerResults_*_HLT', 'keep *_hltTriggerSummaryAOD_*_HLT', 'keep *_gsfElectrons_*_*', 'keep *_gsfElectronCores_*_*',
        'keep *SuperCluster*_*_*_*', 'keep *_electronGsfTracks_*_*', 'keep *_generalTracks_*_*',
        'keep *_ak5PFJets_*_*', 'keep *_particleFlow_*_*', 'keep *_kt6PFJets_rho_*',
        'keep *_offlinePrimaryVertices_*_*', 'keep *_offlineBeamSpot_*_*',
        'keep *_generator_*_*', 'keep *_addPileupInfo_*_*', 'keep *_genParticles_*_*'),
    dropDescendantsOfDroppedBranches=cms.untracked.bool(False))
if isData and opts.json:
    process.source.lumisToProcess = LumiList.LumiList(filename=opts.json).getVLuminosityBlockRange()
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
if isData:
    process.GlobalTag.connect = cms.string('sqlite_file:/opt/cms-opendata-conddb/FT53_V21A_AN6_FULL_data_stripped.db')
    process.GlobalTag.globaltag = 'FT53_V21A_AN6_FULL::All'
else:
    process.GlobalTag.connect = cms.string('sqlite_file:/opt/cms-opendata-conddb/START53_V27_MC_stripped.db')
    process.GlobalTag.globaltag = 'START53_V27::All'
process.wdv3 = cms.EDAnalyzer('WDVv3Analyzer',
    hltThesis=cms.vstring('HLT_Photon36_CaloId10_Iso50_Photon22_CaloId10_Iso50_v', 'HLT_Photon36_CaloId10_Iso50_Photon22_R9Id85_v',
                          'HLT_Photon36_R9Id85_Photon22_CaloId10_Iso50_v', 'HLT_Photon36_R9Id85_Photon22_R9Id85_v'),
    jecName=cms.string('ak5PFL1FastL2L3Residual' if isData else 'ak5PFL1FastL2L3'), lwPdg=cms.int32(9000011),
    isData=cms.bool(isData),
    cleanings=cms.vint32(0) if opts.final else cms.vint32(0, 1, 2, 3),
    fitters=cms.vint32(2) if opts.final else cms.vint32(0, 1, 2))
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.out))
process.p = cms.Path(process.wdv3)
