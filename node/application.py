from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow,QFileDialog,QTreeWidgetItem,QErrorMessage
from PyQt5.QtCore import Qt,QTimer
from configparser import ConfigParser
from network.daemon import NetworkDaemon
import sys,argparse,platform,os
import threading,multiprocessing
import importlib,datetime
" our modules:"
from gui import mainWindow
from node import strings,minerid,config
import miners


class minerApp():
    threadTimer = False
    cpuRun = None
    amdRun = None
    nvRun = None
    minerRunning = False
    miner_id = minerid.minerID()
    pipe_nin,pipe_nou = multiprocessing.Pipe()
    pipe_min,pipe_mou = multiprocessing.Pipe()
    miner_mod = False
    miner = False
    
    def __init__(self):
        self.network = NetworkDaemon()
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.mainWindow = mainWindow.Ui_MainWindow()
        self.mainWindow.setupUi(self.window)
        parser = argparse.ArgumentParser(description="Miner Node QTGUI")
        parser.add_argument('-c', '--config')
        parser.add_argument('-v', dest='verbose', action='store_true')
        args = parser.parse_args()
        """ Connect signals and slots: """
        self.mainWindow.CPU_RUN.clicked.connect(self.toggleCPU)
        self.mainWindow.AMD_RUN.clicked.connect(self.toggleAMD)
        self.mainWindow.NV_RUN.clicked.connect(self.toggleNV)
        self.mainWindow.RUN_ALL.clicked.connect(self.startCPU)
        self.mainWindow.RUN_ALL.clicked.connect(self.startNV)
        self.mainWindow.RUN_ALL.clicked.connect(self.startAMD)
        self.mainWindow.STOP_ALL.clicked.connect(self.stopMiner)
        self.mainWindow.SYNC_CONFIG.clicked.connect(self.syncConfig)
        self.mainWindow.api_connect.clicked.connect(self.startNetwork)
        self.mainWindow.api_disconnect.clicked.connect(self.stopNetwork)
        self.mainWindow.actionExport_Config.triggered.connect(self.saveCfgFile)
        self.mainWindow.actionImport_Config.triggered.connect(self.openCfgFile)
        " Fill text boxes"
        self.mainWindow.os.setText(platform.system())
        
        " Setup platform info display:"
        platNode = self.mainWindow.miner_config.findItems('Platform',Qt.MatchExactly,0)
        if (platform.system() == "Linux"):
            uname = platform.uname()
            platNode[0].addChild(QTreeWidgetItem(["{0} at {1}".format(uname.system,uname.node)],0))
            platNode[0].addChild(QTreeWidgetItem(["Release: {0}".format(uname.release)],0))
            platNode[0].addChild(QTreeWidgetItem(["Version: {0}".format(uname.version)],0))
            platNode[0].addChild(QTreeWidgetItem(["Arch: {0}".format(uname.machine)],0))
        " Populate combo boxes:"
        i = 0
        for d in self.miner_id.ifaces:
            if (d in self.miner_id.ifaceids):
                self.mainWindow.miner_id.addItem("Interface: "+d+" MACADDR: "+self.miner_id.ifaceids[d],i)
            i = i + 1
                
        self.config = config.MinerConfig()
        if (args.config != None):
            self._openCfgFile(args.config)
        self.syncConfigToUI()
        " Connect change in entry values to sync behaviour: "
        self.mainWindow.miner_id.currentIndexChanged.connect(self.syncConfigFromUI)
        self.mainWindow.miner_name.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.enable_api.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.enable_remote_cmd.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.enable_remote_config.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.enable_api.stateChanged.connect(self.toggleNetParams)
        self.mainWindow.enable_remote_cmd.stateChanged.connect(self.toggleNetParams)
        self.mainWindow.enable_remote_config.stateChanged.connect(self.toggleNetParams)
        self.mainWindow.api_endpoint.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.api_use_iam.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_PAYMENT_ADDR.text()
        self.mainWindow.XMR_PASSWORD.text()
        self.mainWindow.XMR_CPU_ENABLE.isChecked()
        self.mainWindow.XMR_CPU_AS.isChecked()
        self.mainWindow.XMR_CPU_THREADS.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_NV_ENABLE.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_NV_AS.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_NV_THREADS.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_NV_BLOCKS.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_AMD_ENABLE.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_AMD_AS.stateChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_AMD_INTENSITY.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_AMD_WORKSIZE.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL0.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL1.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL2.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL3.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL4.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL5.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL6.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL7.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL8.textChanged.connect(self.syncConfigFromUI)
        self.mainWindow.XMR_URL9.textChanged.connect
        self.mainWindow.CPU_HS.display(strings.APP_STRINGS['miner']['idle'])
        self.mainWindow.AMD_HS.display(strings.APP_STRINGS['miner']['idle'])
        self.mainWindow.NV_HS.display(strings.APP_STRINGS['miner']['idle'])
        self.window.setWindowTitle(strings.APP_STRINGS["miner"]["app_name"])
        self.app.aboutToQuit.connect(self.network.quit)
        
        self.mainWindow.T_HS.display(strings.APP_STRINGS['miner']['idle'])
        self.mainWindow.H_HS.display(strings.APP_STRINGS['miner']['idle'])
        """Load config:"""
    """ Change button states given config states"""
    def toggleBtnState(self):
        if (self.config.config["remote"]["enable_api"] == False):
            self.mainWindow.api_connect.setDisabled(True)
            self.mainWindow.api_disconnect.setDisabled(True)
        else:
            self.mainWindow.api_connect.setDisabled(False)
            self.mainWindow.api_disconnect.setDisabled(False)
        if (self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["ENABLE"] == False):
            self.mainWindow.CPU_RUN.setDisabled(True)
            self.stopCPU()
        else:
            self.mainWindow.CPU_RUN.setDisabled(False)
        if (self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["ENABLE"] == False):
            self.mainWindow.NV_RUN.setDisabled(True)
            self.stopNV()
        else:
            self.mainWindow.NV_RUN.setDisabled(False)
        if (self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["ENABLE"] == False):
            self.mainWindow.AMD_RUN.setDisabled(True)
            self.stopAMD()
        else:
            self.mainWindow.AMD_RUN.setDisabled(False)
    
    """ Commit network params"""
    def toggleNetParams(self):
        self.network.enabled = self.mainWindow.enable_api.isChecked()
        self.network.cmd_enabled = self.mainWindow.enable_remote_cmd.isChecked()
        self.network.cfg_enabled = self.mainWindow.enable_remote_config.isChecked()
        
    """ Sync Values TO Config Struct FROM UI: """
    def syncConfigFromUI(self):
        if (self.config.locked == False):
            print(self.config.config["miners"]["XMR"]["XMRIG"]["CPU"])
            self.config.config["miner_id"] = self.mainWindow.miner_id.currentIndex()
            self.config.config["miner_name"] = self.mainWindow.miner_name.text()
            self.config.config["remote"]["enable_api"] = self.mainWindow.enable_api.isChecked()
            self.config.config["remote"]["enable_remote_cmd"] = self.mainWindow.enable_remote_cmd.isChecked()
            self.config.config["remote"]["enable_remote_config"] = self.mainWindow.enable_remote_config.isChecked()
            self.config.config["remote"]["api_endpoint"] = self.mainWindow.api_endpoint.text()
            self.config.config["remote"]["api_use_iam"] = self.mainWindow.api_use_iam.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["PAYMENT_ADDR"] = self.mainWindow.XMR_PAYMENT_ADDR.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["PASSWORD"] = self.mainWindow.XMR_PASSWORD.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["ENABLE"] = self.mainWindow.XMR_CPU_ENABLE.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["AS"] = self.mainWindow.XMR_CPU_AS.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["THREADS"] = self.mainWindow.XMR_CPU_THREADS.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["ENABLE"] = self.mainWindow.XMR_NV_ENABLE.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["AS"] = self.mainWindow.XMR_NV_AS.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["THREADS"] = self.mainWindow.XMR_NV_THREADS.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["BLOCKS"] = self.mainWindow.XMR_NV_BLOCKS.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["ENABLE"]=self.mainWindow.XMR_AMD_ENABLE.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["AS"] = self.mainWindow.XMR_AMD_AS.isChecked()
            self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["INTENSITY"] = self.mainWindow.XMR_AMD_INTENSITY.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["WORKSIZE"] = self.mainWindow.XMR_AMD_WORKSIZE.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL0"] = self.mainWindow.XMR_URL0.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL1"] = self.mainWindow.XMR_URL1.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL2"] = self.mainWindow.XMR_URL2.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL3"] = self.mainWindow.XMR_URL3.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL4"] = self.mainWindow.XMR_URL4.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL5"] = self.mainWindow.XMR_URL5.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL6"] = self.mainWindow.XMR_URL6.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL7"] = self.mainWindow.XMR_URL7.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL8"] = self.mainWindow.XMR_URL8.text()
            self.config.config["miners"]["XMR"]["XMRIG"]["URL9"] = self.mainWindow.XMR_URL9.text()
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["config"]["changed"],10000)
            self.toggleBtnState()
        
        
    """ Sync Values TO UI FROM Config struct:"""
    def syncConfigToUI(self):
        try:
            self.mainWindow.miner_id.setCurrentIndex(self.config.config["miner_id"])
            self.mainWindow.miner_name.setText(self.config.config["miner_name"])
            self.mainWindow.enable_api.setChecked(self.config.config["remote"]["enable_api"])
            self.mainWindow.enable_remote_cmd.setChecked(self.config.config["remote"]["enable_remote_cmd"])
            self.mainWindow.enable_remote_config.setChecked(self.config.config["remote"]["enable_remote_config"])
            self.mainWindow.api_endpoint.setText(self.config.config["remote"]["api_endpoint"])
            self.mainWindow.api_use_iam.setChecked(self.config.config["remote"]["api_use_iam"])
            self.mainWindow.XMR_PAYMENT_ADDR.setText(self.config.config["miners"]["XMR"]["XMRIG"]["PAYMENT_ADDR"])
            self.mainWindow.XMR_PASSWORD.setText(self.config.config["miners"]["XMR"]["XMRIG"]["PASSWORD"])
            self.mainWindow.XMR_CPU_ENABLE.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["ENABLE"])
            self.mainWindow.XMR_CPU_AS.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["AS"])
            self.mainWindow.XMR_CPU_THREADS.setText(self.config.config["miners"]["XMR"]["XMRIG"]["CPU"]["THREADS"])
            self.mainWindow.XMR_NV_ENABLE.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["ENABLE"])
            self.mainWindow.XMR_NV_AS.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["AS"])
            self.mainWindow.XMR_NV_THREADS.setText(self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["THREADS"])
            self.mainWindow.XMR_NV_BLOCKS.setText(self.config.config["miners"]["XMR"]["XMRIG"]["NV"]["BLOCKS"])
            self.mainWindow.XMR_AMD_ENABLE.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["ENABLE"])
            self.mainWindow.XMR_AMD_AS.setChecked(self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["AS"])
            self.mainWindow.XMR_AMD_INTENSITY.setText(self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["INTENSITY"])
            self.mainWindow.XMR_AMD_WORKSIZE.setText(self.config.config["miners"]["XMR"]["XMRIG"]["AMD"]["WORKSIZE"])
            self.mainWindow.XMR_URL0.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL0"])
            self.mainWindow.XMR_URL1.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL1"])
            self.mainWindow.XMR_URL2.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL2"])
            self.mainWindow.XMR_URL3.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL3"])
            self.mainWindow.XMR_URL4.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL4"])
            self.mainWindow.XMR_URL5.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL5"])
            self.mainWindow.XMR_URL6.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL6"])
            self.mainWindow.XMR_URL7.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL7"])
            self.mainWindow.XMR_URL8.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL8"])
            self.mainWindow.XMR_URL9.setText(self.config.config["miners"]["XMR"]["XMRIG"]["URL9"])
            self.toggleBtnState()
        except Exception  as e:
            print("Exception during SYNC TO UI:")
            print(e)
        
    """ Open a config file (dialog):"""
    def openCfgFile(self):
        self.fileDialog = QFileDialog(self.window,'Open Config File',os.getcwd(),"*.json")
        self.fileDialog.setModal(True)
        self.fileDialog.fileSelected.connect(self._openCfgFile)
        self.fileDialog.show()
        
    """ Save Config file:"""
    def saveCfgFile(self):
        self.fileDialog = QFileDialog(self.window,'Save Config File as',os.getcwd(),"*.json")
        self.fileDialog.setModal(True)
        self.fileDialog.fileSelected.connect(self._saveCfgFile)
        self.fileDialog.show()
        
    """ Open a config file (Actual logic):"""
    def _openCfgFile(self,file):
        self.config.locked = True
        try:
            self.fileDialog.close()
        except: pass
        try:
            self.config.load(file)
            self.mainWindow.statusbar.showMessage("Loaded Configufration File: {0}.".format(file),5000)
            self.syncConfigToUI()
            self.toggleNetParams()
            
        except:
            err = QErrorMessage(self.window)
            err.showMessage("Unable to parse config file.")
            err.setModal(True)
            err.show()
        self.config.locked = False
        self.autoExec()
    """ Save a config file (Actual logic):"""
    def _saveCfgFile(self,file):
        try:
            self.fileDialog.close()
        except: pass
        try:
            self.config.save(file)
            self.mainWindow.statusbar.showMessage("Saved Configufration File: {0}.".format(file),5000)
            
        except:
            err = QErrorMessage(self.window)
            err.showMessage("Unable to save config file.")
            err.setModal(True)
            err.show()
            

    """ Auto Execute processes if the configuration specifies them: """
    def autoExec(self):
        """ Support Network Autostart: """
        if (self.config.config["remote"]["enable_api"] == True):
            self.startNetwork()
            

    """ Start network: """
    def startNetwork(self):
        self.network.setup(self.config.config,self.pipe_nou,self.pipe_nin)
        if (self.network.started == False):
             self.network.start()
        self.network.enabled = True
        self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["start"],5000)
        self.mainWindow.api_status_2.setText(strings.APP_STRINGS["net"]["connecting"].format(self.config.config["remote"]["api_endpoint"]))
        self.guiLog(strings.APP_STRINGS["net"]["connecting"].format(self.config.config["remote"]["api_endpoint"]))
        
    """ Start network: """
    def stopNetwork(self):
        self.network.stop()
        self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["stop"],5000)
        self.mainWindow.api_status_2.setText(strings.APP_STRINGS["net"]["disabled"])
        self.guiLog(strings.APP_STRINGS["net"]["disabled"])
    
    """ Start Miner Daemon: """
    def startMiner(self):
        if (self.minerRunning == False):
            self.miner_mod = importlib.import_module('.{0}.{1}.miner'.format(self.config.config["currency"],self.config.config["miner"]),'miners')
            self.miner = self.miner_mod.MinerDaemon()
            self.miner.setup(self.config.config["miners"][self.config.config["currency"]][self.config.config["miner"]],self.pipe_mou,self.pipe_min)
            self.app.aboutToQuit.connect(self.miner.quit)
            self.miner.start()
            self.minerRunning = True
            self.mainWindow.T_HS.display(0)
            self.mainWindow.H_HS.display(0)

    """ Logging Facility: """
    def guiLog(self,msg,type=0):
        ts = datetime.datetime.now()
        if (type == 0):
            cmsg = "<b>[{0}]</b> {1}<br/>\n".format(ts.strftime("%Y-%m-%d %H:%M:%S"),msg);
        elif (type == 1):
             cmsg = "<b><font color=\"#bca371\"> [{0}] WARN:</b> {1}</font><br/>\n".format(ts.strftime("%Y-%m-%d %H:%M:%S"),msg);
        elif (type == 2):
            cmsg = "<b><font color=\"#c97064\"> [{0}] ERROR:</b> {1}</font><br/>\n".format(ts.strftime("%Y-%m-%d %H:%M:%S"),msg);
        elif (type == 3):
            cmsg = "<b>[{0}]<font color=\"#3f8482\"> Hashrates:</b> {1}</font><br/>\n".format(ts.strftime("%Y-%m-%d %H:%M:%S"),msg);
        else:
            cmsg = msg
        self.mainWindow.MINER_LOG.append(cmsg)
    """ Stop Miner Daemon: """
    def stopMiner(self):
        if (self.minerRunning == True):
            if (self.cpuRun == True): self.stopCPU()
            if (self.nvRun == True): self.stopNV()
            if (self.amdRun == True): self.stopAMD()
            self.miner.exec = False
            self.minerRunning = False
            

    """ Stop CPU Miner: """
    def stopCPU(self):
        if (self.cpuRun != False):
            self.mainWindow.CPU_HS.display(strings.APP_STRINGS['miner']['idle'])
            self.mainWindow.CPU_RUN.setText(strings.APP_STRINGS["miner"]["start"])
            self.cpuRun = False
            self.miner.exec_cpu = False
            self.totalDispReset()
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["STOP-CPU"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["STOP-CPU"])
        
    """ Start CPU Miner: """
    def startCPU(self):
        if (self.mainWindow.XMR_CPU_ENABLE.isChecked() == False): return True
        if (self.cpuRun != True):
            self.startMiner()
            self.mainWindow.CPU_HS.display(0)
            self.mainWindow.CPU_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.cpuRun = True
            self.miner.exec_cpu = True
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["START-CPU"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["START-CPU"])
            
    """ Glue for CPU  """    
    def toggleCPU(self):
        if (self.cpuRun is  True):
            self.stopCPU()
        else:
            self.startCPU()

    """ Stop NV Miner: """
    def stopNV(self):
        if (self.nvRun != False):
            self.mainWindow.NV_HS.display(strings.APP_STRINGS['miner']['idle'])
            self.mainWindow.NV_RUN.setText(strings.APP_STRINGS["miner"]["start"])
            self.nvRun = False
            self.miner.exec_nv = False
            self.totalDispReset()
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["STOP-NV"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["STOP-NV"])
        
    """ Start NV Miner: """
    def startNV(self):
        if (self.mainWindow.XMR_NV_ENABLE.isChecked() == False): return True
        if (self.nvRun != True):
            self.startMiner()
            self.mainWindow.NV_HS.display(0)
            self.mainWindow.NV_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.nvRun = True
            self.miner.exec_nv = True
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["START-NV"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["START-NV"])
                       
    """ Glue for NV  """    
    def toggleNV(self):
        if (self.nvRun is  True):
            self.stopNV()
        else:
            self.startNV()
            
        """ Stop AMD Miner: """
    def stopAMD(self):
        if (self.amdRun != False):
            self.mainWindow.AMD_HS.display(strings.APP_STRINGS['miner']['idle'])
            self.mainWindow.AMD_RUN.setText(strings.APP_STRINGS["miner"]["start"])
            self.miner.exec_amd = False
            self.totalDispReset()
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["STOP-AMD"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["STOP-AMD"])
        
    """ Start AMD Miner: """
    def startAMD(self):
        if (self.mainWindow.XMR_AMD_ENABLE.isChecked() == False): return True
        if (self.amdRun != True):
            self.startMiner()
            self.mainWindow.AMD_HS.display(0)
            self.mainWindow.AMD_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.amdRun = True
            self.miner.exec_amd = True
            self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["status"]["START-AMD"],5000)
            self.guiLog(strings.APP_STRINGS["status"]["START-AMD"])
            
            
    """ Glue for AMD  """    
    def toggleAMD(self):
        if (self.amdRun is  True):
            self.stopAMD()
        else:
            self.startAMD()
            
    """ Glue for Sync Config: """
    def syncConfig(self):
        self.stopMiner()
        self.startMiner()
        
    def totalDispReset(self):
        if ((self.amdRun is False) and (self.cpuRun is False) and (self.nvRun is False)):
            self.mainWindow.T_HS.display(strings.APP_STRINGS['miner']['idle'])
            self.mainWindow.H_HS.display(strings.APP_STRINGS['miner']['idle'])


    """ Update UI:"""
    def updateUI(self,event):
        self.miner.logParser.reset()
        if (self.cpuRun is False): self.mainWindow.CPU_HS.display(strings.APP_STRINGS["miner"]["idle"])
        if (self.nvRun is False): self.mainWindow.NV_HS.display(strings.APP_STRINGS["miner"]["idle"])
        if (self.amdRun is False): self.mainWindow.AMD_HS.display(strings.APP_STRINGS["miner"]["idle"])
        if 'payload' in event:
            if 'method' in event:
                """ Depending on event, update UI: """
                if event["method"] == "TOTALS":
                    self.mainWindow.CPU_HS.display(event["payload"]["c"])
                    self.mainWindow.NV_HS.display(event["payload"]["n"])
                    self.mainWindow.AMD_HS.display(event["payload"]["a"])
                    if (event["payload"]["t"] > 0.1):
                        self.mainWindow.T_HS.display(event["payload"]["t"])
                    if (event["payload"]["h"] > 0.1):
                        self.mainWindow.H_HS.display(event["payload"]["h"])
                    log_msg = "<br/>CPU: {0} H/s, NV: {1} H/s AMD: {2} H/s<br/> Total: {3} H/s, Highest: {4} H/s".format(event["payload"]["c"],event["payload"]["n"],event["payload"]["a"],event["payload"]["t"],event["payload"]["h"])
                    self.window.setWindowTitle(strings.APP_STRINGS["miner"]["app_name"]+" : Total {0} H/s (CPU: {1} H/s NV: {2} H/s AMD: {3} H/s) Highest: {4} H/s".format(event["payload"]["t"],event["payload"]["c"],event["payload"]["n"],event["payload"]["a"],event["payload"]["h"]))
                    self.guiLog(log_msg,3)
                elif event["method"] == "TYPE":
                    if "payload" in event:
                        if event["payload"]["typeof"] == "cpu":
                            platNode = self.mainWindow.miner_config.findItems('CPU(s)',Qt.MatchExactly,0)
                            platNode[0].addChild(QTreeWidgetItem(["CPU: {1}: {0}".format(event["payload"]["cputype"],event["payload"]["cpucount"])],0))
                            self.guiLog("CPU {1}: {0}".format(event["payload"]["cputype"],event["payload"]["cpucount"]))
                        
                elif event["method"] == "WARNING":
                    print(event)
                    if event["value"] in self.strings.APP_STRINGS["warn"]:
                        self.mainWindow.statusbar.showMessage("WARNING: {0}".format(self.strings.APP_STRINGS["warn"][event["value"]]),5000)
    
    
    
    
    
    """"Process events incoming and outgoing, Miner and network:"""
    def processEvents(self):


        """ Incoming Network events: """
        while (self.pipe_nou.poll()>0):
            msg = self.pipe_nou.recv()
            if "type" in msg:
                if (msg["type"] == "err"):
                    self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["err"][msg["err"]],5000)
                elif (msg["type"] == "status"):
                    self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["status"][msg["msg"]],5000)
                    if (msg['msg'] == 'AUTH-OK'):
                        self.mainWindow.api_status_2.setText(strings.APP_STRINGS["net"]["connected"])
                        self.guiLog(strings.APP_STRINGS["net"]["connected"])
        while (self.pipe_mou.poll()>0):
            msg = self.pipe_mou.recv()
            """ Send incoming network events to the Network daemon if enabled, and the UI updater thread"""
            self.updateUI(msg)
            if (self.network.auth is True):
                self.pipe_nou.send(msg)
    
    """ Main Exec Thread: """
    def run(self):
        self.window.show()
        self.threadTimer = QTimer()
        self.threadTimer.timeout.connect(self.processEvents)
        self.threadTimer.start(1000)
        sys.exit(self.app.exec_())


