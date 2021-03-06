import FWCore.ParameterSet.Config as cms

### CMSSW command line parameter parser                                                                                                                                        
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')

options.register (
        'delayStep',0,VarParsing.multiplicity.singleton,VarParsing.varType.int,
        'integer numer to identify the delay xml for each partition');

options.register ('eventToSkip',0,VarParsing.multiplicity.singleton,VarParsing.varType.int,
                  'interget number to indicate how many events to skip')


options.register ('secondaryFiles',[],VarParsing.multiplicity.list,VarParsing.varType.string,
                  'list of secondary files')

options.register ('ouputFileName',"trackerDPG.root",VarParsing.multiplicity.singleton,VarParsing.varType.string,
                  'name of the outtput root file')

options.register ('jsonFile',"",VarParsing.multiplicity.singleton,VarParsing.varType.string,
                  'json file to apply')

options.register ('isRawFile',False,VarParsing.multiplicity.singleton,VarParsing.varType.bool,
                  'when running as input a raw file instead of a standard FEVT')

options.register ('isDatFile',False,VarParsing.multiplicity.singleton,VarParsing.varType.bool,
                  'when running as input a dat file file instead of a standard FEVT')


options.parseArguments()

### start cmssw job
import FWCore.PythonUtilities.LumiList as LumiList
from Configuration.StandardSequences.Eras import eras

process = cms.Process("clusterAnalysis",eras.Run2_2016)
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
readFiles = cms.untracked.vstring(options.inputFiles)
secFiles  = cms.untracked.vstring(options.secondaryFiles) 

if not options.isDatFile:
    process.source = cms.Source ("PoolSource",fileNames = readFiles, secondaryFileNames = secFiles)
    process.source.skipEvents = cms.untracked.uint32(options.eventToSkip)
else:
    process.source = cms.Source("NewEventStreamFileReader",
                                fileNames = readFiles)
    process.source.skipEvents = cms.untracked.uint32(options.eventToSkip)

if options.jsonFile != "":
    process.source.lumisToProcess = LumiList.LumiList(filename = options.jsonFile).getVLuminosityBlockRange()

# Conditions (Global Tag is used here):
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data_GRun', '')
#process.GlobalTag.globaltag = '80X_dataRun2_Express_v4'

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True))

#Geometry and field
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")
process.load("Geometry.CommonDetUnit.globalTrackingGeometryDB_cfi")
process.load("TrackingTools.RecoGeometry.RecoGeometries_cff")

process.load("RecoTracker.MeasurementDet.MeasurementTrackerEventProducer_cfi")
## from Vincenzo Innocente: http://cmslxr.fnal.gov/lxr/source/RecoTracker/TrackProducer/test/TrackRefit.py?v=CMSSW_8_1_0_pre2

## re-fit only when starting from raw-reco of FEVT
if not options.isRawFile and not options.isDatFile:
    process.load("RecoTracker.TrackProducer.TrackRefitter_cfi")
    process.load('RecoTracker.TrackProducer.TrackRefitters_cff')
    process.TrackRefitter.NavigationSchool = ''
    process.TrackRefitter.Fitter = 'FlexibleKFFittingSmoother'
    process.ttrhbwr.ComputeCoarseLocalPositionFromDisk = True
    process.generalTracksFromRefit = process.TrackRefitter.clone(
        src = cms.InputTag("generalTracks")
        )
    
    process.doAlldEdXEstimators += process.dedxMedian

    process.dedxTruncated40.tracks = "generalTracksFromRefit"
    process.dedxTruncated40.trajectoryTrackAssociation = "generalTracksFromRefit"
    process.dedxHarmonic2.tracks = "generalTracksFromRefit"
    process.dedxHarmonic2.trajectoryTrackAssociation = "generalTracksFromRefit"
    process.dedxMedian.tracks = "generalTracksFromRefit"
    process.dedxMedian.trajectoryTrackAssociation = "generalTracksFromRefit"
    process.dedxHitInfo.tracks = "generalTracksFromRefit"
    process.dedxHitInfo.trajectoryTrackAssociation = "generalTracksFromRefit"
    process.refit = cms.Sequence(process.MeasurementTrackerEvent*process.generalTracksFromRefit*process.doAlldEdXEstimators)


### Analyzer
process.analysis = cms.EDAnalyzer('TrackerDpgAnalysis',
   ClustersLabel = cms.InputTag("siStripClusters"),
   PixelClustersLabel = cms.InputTag("siPixelClusters"),
   TracksLabel   = cms.VInputTag( cms.InputTag("generalTracksFromRefit")),
   vertexLabel   = cms.InputTag('offlinePrimaryVertices'),
   pixelVertexLabel = cms.InputTag('pixelVertices'),
   beamSpotLabel = cms.InputTag('offlineBeamSpot'),
   DeDx1Label    = cms.InputTag('dedxHarmonic2'),
   DeDx2Label    = cms.InputTag('dedxTruncated40'),
   DeDx3Label    = cms.InputTag('dedxMedian'),
   L1Label       = cms.InputTag('gtDigis'),
   HLTLabel      = cms.InputTag("TriggerResults::HLT"),
   InitalCounter = cms.uint32(1),
   keepOntrackClusters  = cms.untracked.bool(True),
   keepOfftrackClusters = cms.untracked.bool(False),
   keepPixelClusters    = cms.untracked.bool(False),
   keepPixelVertices    = cms.untracked.bool(False),
   keepMissingHits      = cms.untracked.bool(False),
   keepTracks           = cms.untracked.bool(True),
   keepVertices         = cms.untracked.bool(True),
   keepEvents           = cms.untracked.bool(True),
   DelayFileNames = cms.untracked.vstring(
        "TI_27-JAN-2010_2_delaystep"+str(options.delayStep)+".xml",
        "TO_30-JUN-2009_1_delaystep"+str(options.delayStep)+".xml",
        "TP_09-JUN-2009_1_delaystep"+str(options.delayStep)+".xml",
        "TM_09-JUN-2009_1_delaystep"+str(options.delayStep)+".xml",
   )
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(options.ouputFileName)
)

process.skimming = cms.EDFilter("PhysDecl",
  applyfilter = cms.untracked.bool(False),
  debugOn = cms.untracked.bool(False),
  HLTriggerResults = cms.InputTag("TriggerResults","","HLT")

)

if options.isRawFile or options.isDatFile:
    process.load('Configuration.StandardSequences.RawToDigi_cff')    
    process.load('Configuration.StandardSequences.Reconstruction_cff')
    process.load('RecoTracker.DeDx.dedxEstimators_cff')
    process.analysis.TracksLabel = cms.VInputTag(cms.InputTag("generalTracks"))
    process.p = cms.Path(process.RawToDigi*
                         process.reconstruction_trackingOnly* ## local and gloabl reco
                         process.doAlldEdXEstimators*
                         process.skimming*
                         process.dedxMedian*
                         process.analysis)

else:
    process.p = cms.Path(process.skimming*process.refit*process.analysis)

processDumpFile = open('processDump.py', 'w')
print >> processDumpFile, process.dumpPython()
