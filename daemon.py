
from logparser import MinerParser
import os,sys
from time import sleep
from minercfg import MinerCFG
import platform
import threading
import subprocess
import logging
logging.basicConfig(level=logging.INFO)
class MinerDaemon(threading.Thread):
    ''' Variables: '''
    exec = True
    config = False
    miner_cfg = False
    cwd = False
    pt = False
    ''' File pointers: '''
    log_cpu = False
    log_nv = False
    log_amd = False
    
    ''' Processes'''
    cpu = False
    nv = False
    amd = False
    
    
    ''' Network IO: '''
    network = False
    parser = MinerParser()
    ''' functions: '''
    
    
    '''Logging:'''
    log = logging.getLogger('miner_node')
    ''' Prepare log files: '''
    def mkcpulog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["CPU"]["log"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["CPU"]["log"]
    
        try:
            self.log.info("CPU LOG PATH: {0}".format(path))
            self.log_cpu = open(path,"wt+")
        except Exception as e:
            self.log.error("Unable to create CPU Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()

    def mknvlog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["NVIDIA"]["log"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["NVIDIA"]["log"]
        try:
            self.log.info("NVIDIA LOG PATH: {0}".format(path))
            self.log_nv = open(path,"tw+")
        except Exception as e:
            self.log.error("Unable to create NVIDIA Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()

    def mkamdlog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["AMD"]["log"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["AMD"]["log"]
        try:
            self.log.info("AMD LOG PATH: {0}".format(path))
            self.log_amd = open(path,"tw+")
        except Exception as e:
            self.log.error("Unable to create AMD Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()
            
     
     
    ''' Functions to [re]start and stop different miners:'''
    def startCPU(self):
        try:
            self.log_cpu.close()
        except: pass
        self.mkcpulog()
        self.miner_cfg.mkCPU()
        self.log.info("Attempting to start CPU Miner")
        if (self.pt == "linux"):
            self.log.info("CPU Miner Command: ./xmrig-cpu -c {0} (CWD: {1})".format(self.config["CPU"]["config"],self.cwd))
            self.cpu = subprocess.Popen(["./xmrig-cpu","-c",self.config["CPU"]["config"]],bufsize=1024,cwd=self.cwd+"/bin/linux/",universal_newlines=True)
            self.log.info("CPU Miner Started.")
        if (self.pt =="win"):
            self.log.info("CWD: {0}".format(self.cwd+"\\bin\win\\"))
            self.log.info('CPU Miner command: xmrig.exe -c {0}'.format(self.config["CPU"]["config"],self.cwd))
            self.cpu = subprocess.Popen(["xmrig.exe","-c",self.config["CPU"]["config"]],bufsize=1024,cwd=self.cwd+'\\bin\win\\',universal_newlines=True,shell=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
            self.log.info("CPU Miner Started.")
                
    def stopCPU(self):
        try:
            self.cpu.kill()
            self.log_cpu.close()
            self.log.info("CPU Miner Stopped.")  
        except: 
            pass
    

    def startNV(self):
        try:
            self.log_nv.close()
        except: pass
        self.mknvlog()
        self.miner_cfg.mkNV()
        self.log.info("Attempting to start NVidia Miner")
        if (self.pt == "linux"):
            self.log.info("NVidia Miner command: ./xmrig-nvidia -c {0}".format(self.config["NVIDIA"]["config"],self.cwd))
            self.nv = subprocess.Popen(["./xmrig-nvidia","-c",self.config["NVIDIA"]["config"]],bufsize=1024,cwd=self.cwd+"/bin/linux/",universal_newlines=True)
            self.log.info("Nvidia Miner Started.")
        if (self.pt =="win"):
            self.log.info("CWD: {0}".format(self.cwd+"\\bin\win\\"))
            self.log.info("NVidia Miner command: xmrig-nvidia.exe -c {0} --cuda-launch={1}x{2}".format(self.config["NVIDIA"]["config"],self.config["NVIDIA"]["threads"],self.config["NVIDIA"]["blocks"]))
            self.nv = subprocess.Popen(["xmrig-nvidia.exe","-c",self.config["NVIDIA"]["config"],"--cuda-launch={0}x{1}".format(self.config["NVIDIA"]["threads"],self.config["NVIDIA"]["blocks"])],bufsize=1024,cwd=self.cwd+"\\bin\win\\",universal_newlines=True,shell=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
            self.log.info("Nvidia Miner Started.")

    def stopNV(self):
        try:
            self.nv.kill()
            self.log_nv.close()
            self.log.info("Nvidia Miner Stopped.")   
        except: 
            pass
    

        
    def startAMD(self):
        self.log.info("Attempting to start AMD Miner")
        try:
            self.log_amd.close()
        except: pass
        self.mkamdlog()
        self.miner_cfg.mkAMD()
        if (self.pt == "lin"):
            self.log.info("AMD Miner command: ./xmrig-amd -c {0}".format(self.config["AMD"]["config"],self.cwd))
            self.nv = subprocess.Popen(["./xmrig-amd","-c",self.config["AMD"]["config"]],bufsize=1024,cwd=self.cwd+"/bin/linux/",universal_newlines=True)
            self.log.info("AMD Miner Started.")
        if (self.pt == "win"):
            self.log.info("CWD: {0}".format(self.cwd+"\\bin\win\\"))
            self.log.info("AMD Miner command: xmrig-amd.exe -c {0}".format(self.config["AMD"]["config"],self.cwd))
            self.amd = subprocess.Popen(["xmrig-amd.exe","-c",self.config["AMD"]["config"]],bufsize=1024,cwd=self.cwd+"\\bin\win\\",universal_newlines=True,shell=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
            self.log.info("AMD Miner Started.")
    def stopAMD(self):
        try:
            self.amd.kill()
            self.log_amd.close()
            self.log.info("AMD stopped.")   
        except: 
            pass
    
    
    def processOutput(self):
        ''' Process output from CPU first: '''
        if (self.cpu != False):
            line = None
            while (line != ''):
                rev = self.parser.parseCPU(line)
                if (type(rev) == dict):
                    ''' Depending on what the parser replied, send information to the endpoint: '''
                    if ("warn" in rev):
                        self.log.warn("Warning: {0}".format(rev["value"]))
                        print({"method":"WARNING","type":rev["warn"],"value":rev["value"]})
                    if ("type" in rev):
                        if (rev["type"] == "cpu"):
                            self.network.send({"method":"TYPE","payload":{"typeof":"cpu","cputype":rev["value"],"cpucount":1,"os":self.pt}})
                line = self.log_cpu.readline()
        ''' Process output from NVidia : '''
        if (self.nv != False):
            line = None
            while (line != ''):
                self.parser.parseNV(line)
                line = self.log_nv.readline()
        ''' Process output from AMD : '''
        if (self.amd != False):
            line = None
            while (line != ''):
                self.parser.parseAMD(line)
                line = self.log_amd.readline()
        total = self.parser.getTotal()
        
        if (total['t'] != 0):
            self.network.send({"method":"TOTALS","payload":total})
        speeds = self.parser.getSpeed()
        self.network.send({"method":"SPEED","payload":speeds})
        
                
    def setup(self,config,netpipe):
        self.config = config
        self.network = netpipe
        self.log.info("Miner_node: Miner ID {0}, Wallet: {1}, MinerName: {2}".format(self.config["GLOBAL"]["minerid"],self.config["POOLS"]["payment"],self.config["POOLS"]["minerName"]))
        self.cwd = os.getcwd()
        self.miner_cfg = MinerCFG(self.config)
        plat = platform.system()
        if (plat == "Linux"):
            self.pt = "linux"
        elif (plat == "Windows"):
            self.pt = "win"
        #self.mkLogs()
        #if (self.config["CPU"]["enable"] is "1"):
        #    self.miner_cfg.mkCPU()
        #if (self.config["NVIDIA"]["enable"] is "1"):
        #    self.miner_cfg.mkNV()        
        #if (self.config["AMD"]["enable"] is "1"):
        #    self.miner_cfg.mkAMD()

    def run(self):
        self.log.info("Starting Execution")
        while (self.exec is True):
            ''' Keep Miners busy: '''
            '''CPU:'''
            if (self.config["CPU"]["enable"] is "1"):
                if (self.cpu == False):
                    self.startCPU()
                else:
                    if (self.cpu.poll() != None):
                        self.log.warning("CPU Miner has exited; restart...")
                        self.startCPU()
            else:
                if (self.cpu != False):
                    self.cpu.kill()
                    self.cpu = False
            '''NVIDIA:'''
            if (self.config["NVIDIA"]["enable"] is "1"):
                if (self.nv == False):
                    self.startNV()
                else:
                    if (self.nv.poll() != None):
                        self.log.warning("NVIDIA Miner has exited; restart...")
                        self.startNV()
            else:
                if (self.nv != False):
                    self.nv.kill()
                    self.nv = False
            '''AMD:'''
            if (self.config["AMD"]["enable"] is "1"):
                if (self.amd == False):
                    self.startAMD()
                else:
                    if (self.amd.poll() != None):
                        self.log.warning("AMD Miner has exited; restart...")
                        self.startAMD()
            else:
                if (self.amd != False):
                    self.amd.kill()
                    self.amd = False
            ''' Process outputs: '''

            self.processOutput()
            sleep(int(self.config['GLOBAL']['sleep']))
