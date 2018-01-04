from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow,QFileDialog,QTreeWidgetItem,QErrorMessage
from PyQt5.QtCore import Qt,QTimer
from configparser import ConfigParser
from network.daemon import NetworkDaemon
import sys,argparse,platform,os
import threading,multiprocessing
" our modules:"
from gui import mainWindow
from node import strings,minerid,config



class minerApp():
    cpuRun = None
    amdRun = None
    nvRun = None
    threadTimer = False
    miner_id = minerid.minerID()
    pipe_nin,pipe_nou = multiprocessing.Pipe()

    
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
        self.mainWindow.STOP_ALL.clicked.connect(self.stopCPU)
        self.mainWindow.STOP_ALL.clicked.connect(self.stopNV)
        self.mainWindow.STOP_ALL.clicked.connect(self.stopAMD)
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
        self.mainWindow.XMR_URL9.textChanged.connect(self.syncConfigFromUI)
        self.stopCPU()
        self.stopNV()
        self.stopAMD()
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
            self.mainWindow.statusbar.showMessage("Loaded Configufration File: {0}.".format(file))
            self.syncConfigToUI()
            self.toggleNetParams()
            
        except:
            err = QErrorMessage(self.window)
            err.showMessage("Unable to parse config file.")
            err.setModal(True)
            err.show()
        self.config.locked = False
        self.autoExec()


    """ Auto Execute processes if the configuration specifies them: """
    def autoExec(self):
        """ Support Network Autostart: """
        if (self.config.config["remote"]["enable_api"] == True):
            self.startNetwork()
            
    """ Save a config file (Actual logic):"""
    def _saveCfgFile(self,file):
        try:
            self.fileDialog.close()
        except: pass
        try:
            self.config.save(file)
            self.mainWindow.statusbar.showMessage("Saved Configufration File: {0}.".format(file))
            
        except:
            err = QErrorMessage(self.window)
            err.showMessage("Unable to save config file.")
            err.setModal(True)
            err.show()
            
    """ Start network: """
    def startNetwork(self):
        self.network.setup(self.config.config,self.pipe_nin,self.pipe_nou)
        if (self.network.started == False):
             self.network.start()
        self.network.enabled = True
        self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["start"])
        self.mainWindow.api_status_2.setText(strings.APP_STRINGS["net"]["connecting"].format(self.config.config["remote"]["api_endpoint"]))
        
    """ Start network: """
    def stopNetwork(self):
        self.network.stop()
        self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["stop"])
        self.mainWindow.api_status_2.setText(strings.APP_STRINGS["net"]["disabled"])
        
    """ Stop CPU Miner: """
    def stopCPU(self):
        if (self.cpuRun != False):
            self.mainWindow.CPU_HS.display(strings.APP_STRINGS['miner']['idle'])
            self.mainWindow.CPU_RUN.setText(strings.APP_STRINGS["miner"]["start"])
            self.cpuRun = False
        
    """ Start CPU Miner: """
    def startCPU(self):
        if (self.mainWindow.XMR_CPU_ENABLE.isChecked() == False): return True
        if (self.cpuRun != True):
            self.mainWindow.CPU_HS.display(0)
            self.mainWindow.CPU_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.cpuRun = True
            
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
        
    """ Start NV Miner: """
    def startNV(self):
        if (self.mainWindow.XMR_NV_ENABLE.isChecked() == False): return True
        if (self.nvRun != True):
            self.mainWindow.NV_HS.display(0)
            self.mainWindow.NV_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.nvRun = True
            
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
            self.amdRun = False
        
    """ Start AMD Miner: """
    def startAMD(self):
        if (self.mainWindow.XMR_AMD_ENABLE.isChecked() == False): return True
        if (self.amdRun != True):
            self.mainWindow.AMD_HS.display(0)
            self.mainWindow.AMD_RUN.setText(strings.APP_STRINGS["miner"]["stop"])
            self.amdRun = True
            
    """ Glue for AMD  """    
    def toggleAMD(self):
        if (self.amdRun is  True):
            self.stopAMD()
        else:
            self.startAMD()
    
    """"Process events incoming and outgoing, Miner and network:"""
    def processEvents(self):
        """ Incoming Network events: """
        while (self.pipe_nou.poll()>0):
            msg = self.pipe_nou.recv()
            if (msg["type"] == "err"):
                self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["err"][msg["err"]])
            elif (msg["type"] == "status"):
                self.mainWindow.statusbar.showMessage(strings.APP_STRINGS["net"]["status"][msg["msg"]])
    
    
    """ Main Exec Thread: """
    def run(self):
        self.window.show()
        self.threadTimer = QTimer()
        self.threadTimer.timeout.connect(self.processEvents)
        self.threadTimer.start(1000)
        sys.exit(self.app.exec_())


