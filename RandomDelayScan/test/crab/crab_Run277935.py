from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB

config = config()

#### Basic crab config structure
config.General.requestName  = 'delaySCAN_Express_Run277935'
config.General.transferLogs = False
config.General.workArea     = 'crab_trackerDPG'  # Make sure you set this parameter

config.JobType.psetName         = 'trackerdpganalysis_cfg.py'
config.JobType.pyCfgParams      = ['delayStep=7']
config.JobType.pluginName       = 'Analysis'
config.JobType.outputFiles      = ['trackerDPG.root']
config.JobType.allowUndistributedCMSSW = True
config.JobType.numCores         = 1
config.JobType.inputFiles       = ['TI_27-JAN-2010_2_delaystep7.xml','TM_09-JUN-2009_1_delaystep7.xml','TO_30-JUN-2009_1_delaystep7.xml','TP_09-JUN-2009_1_delaystep7.xml','PSUmapping.csv']

config.Data.inputDataset  = '/ExpressPhysics/Run2016F-Express-v1/FEVT' 
config.Data.inputDBS      = 'global'
config.Data.splitting     = 'LumiBased'
config.Data.unitsPerJob   = 3
config.Data.outLFNDirBase = '/store/user/rgerosa/TrackerDAQ/DELAYSCAN/'
config.Data.allowNonValidInputDataset = True
config.Data.publication   = False
config.Data.lumiMask      = '/afs/cern.ch/user/r/rgerosa/work/TrackerDAQ/DELAY_SCAN/CMSSW_8_0_14/src/DPGAnalysis/SiStripTools/test/crab/json_277935.txt'

config.Site.storageSite = 'T2_CH_CERN'

