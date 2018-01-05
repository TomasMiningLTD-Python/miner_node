import os
import sys
import time
import platform
import threading
import subprocess
import logging
from miners.XMR.XMRIG import logParser,minercfg
logging.basicConfig(level=logging.INFO)
class MinerDaemon(threading.Thread):
    exec = True
    ''' File pointers: '''
    log_cpu = False
    log_nv = False
    log_amd = False
    
    ''' Processes'''
    cpu = False
    nv = False
    amd = False
    
    exec_cpu = False
    exec_nv = False
    exec_amd = False
    logParser = logParser.MinerParser()
    log = logging.getLogger('miner_node/XMR/XMRIG')
    def setup(self,config,pipe_in,pipe_out):
        self.config = config
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.minercfg = minercfg.MinerCFG(self.config)
        self.log.info("Wallet: {0}, MinerName:{1}".format(self.config["PAYMENT_ADDR"],self.config["PASSWORD"]))
        self.cwd = os.getcwd()
        plat = platform.system()
        if (plat == "Linux"):
            self.pt = "linux"
        elif (plat == "Windows"):
            self.pt = "win"
        self.cwd = os.getcwd()
            
    def mkcpulog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["CPU"]["LOG"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["CPU"]["LOG"]
    
        try:
            self.log.info("CPU LOG PATH: {0}".format(path))
            self.log_cpu = open(path,"wt+")
        except Exception as e:
            self.log.error("Unable to create CPU Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()

    def mknvlog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["NV"]["LOG"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["NV"]["LOG"]
        try:
            self.log.info("NVIDIA LOG PATH: {0}".format(path))
            self.log_nv = open(path,"tw+")
        except Exception as e:
            self.log.error("Unable to create NVIDIA Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()

    def mkamdlog(self):
        if (self.pt == "linux"):
            path = self.cwd+"/log/"+self.config["AMD"]["LOG"]
        elif (self.pt == "win"):
            path = self.cwd+"\\log\\"+self.config["AMD"]["LOG"]
        try:
            self.log.info("AMD LOG PATH: {0}".format(path))
            self.log_amd = open(path,"tw+")
        except Exception as e:
            self.log.error("Unable to create AMD Log file {0}!!".format(path))
            self.log.error(e)
            sys.exit()
    
    def processOutput(self):
        ''' Process output from CPU first: '''
        if (self.cpu != False):
            line = None
            while (line != ''):
                rev = self.logParser.parseCPU(line)
                if (type(rev) == dict):
                    ''' Depending on what the parser replied, send information to the endpoint: '''
                    if ("warn" in rev):
                        self.log.warn("Warning: {0}".format(rev["value"]))
                        print({"method":"WARNING","type":rev["warn"],"value":rev["value"]})
                    if ("type" in rev):
                        if (rev["type"] == "cpu"):
                            self.pipe_out.send({"method":"TYPE","payload":{"typeof":"cpu","cputype":rev["value"],"cpucount":1,"os":self.pt}})
                line = self.log_cpu.readline()
        ''' Process output from NVidia : '''
        if (self.nv != False):
            line = None
            while (line != ''):
                self.logParser.parseNV(line)
                line = self.log_nv.readline()
        ''' Process output from AMD : '''
        if (self.amd != False):
            line = None
            while (line != ''):
                self.logParser.parseAMD(line)
                line = self.log_amd.readline()
        total = self.logParser.getTotal()
        
        if (total['t'] != 0):
            self.pipe_out.send({"method":"TOTALS","payload":total})
        speeds = self.logParser.getSpeed()
        self.pipe_out.send({"method":"SPEED","payload":speeds})
        
        
    
    def startCPU(self):
        try:
            self.log_cpu.close()
        except: pass
        self.mkcpulog()
        self.minercfg.mkCPU()
        self.log.info("Attempting to start CPU Miner")
        if (self.pt == "linux"):
            self.log.info("CPU Miner Command: ./xmrig-cpu -c {0}/tmp/cpu.json ".format(self.cwd+"/miners/XMR/XMRIG/linux/"))
            self.cpu = subprocess.Popen(["./xmrig-cpu","-c",'{0}/tmp/cpu.json'.format(self.cwd)],bufsize=1024,cwd=self.cwd+"/miners/XMR/XMRIG/linux/",universal_newlines=True)
            self.log.info("CPU Miner Started.")
        if (self.pt =="win"):
            self.log.info('CPU Miner command: xmrig-cpu.exe -c {0}\\tmp\\cpu.json'.format(self.cwd+'\\miners\\XMR\\XMRIG\\win\\'))
            self.cpu = subprocess.Popen(["xmrig-cpu.exe","-c","{0}\\tmp\\cpu.json".format(self.cwd)],bufsize=1024,cwd=self.cwd+'\\miners\\XMR\\XMRIG\\win\\',universal_newlines=True,shell=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
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
        self.minercfg.mkNV()
        self.log.info("Attempting to start NV Miner")
        if (self.pt == "linux"):
            self.log.info("NV Miner Command: ./xmrig-nv -c {0}/tmp/nv.json --cuda-launch={1}x{2}".format(self.cwd+"/miners/XMR/XMRIG/linux/",self.config["NV"]["THREADS"],self.config["NV"]["BLOCKS"]))
            self.nv = subprocess.Popen(["./xmrig-nv","-c",'{0}/tmp/nv.json'.format(self.cwd),"--cuda-launch={0}x{1}".format(self.config["NV"]["THREADS"],self.config["NV"]["BLOCKS"])],bufsize=1024,cwd=self.cwd+"/miners/XMR/XMRIG/linux/",universal_newlines=True)
            self.log.info("NV Miner Started.")
        if (self.pt =="win"):
            self.log.info("NV Miner command: xmrig-nv.exe -c {0}\\tmp\\nv.json --cuda-launch={1}x{2}".format(self.cwd+"\\miners\\XMR\\XMRIG\\linux\\",self.config["NV"]["THREADS"],self.config["NV"]["BLOCKS"]))
            self.nv = subprocess.Popen(["xmrig-nv.exe","-c","{0}\\tmp\\nv.json".format(self.cwd),"--cuda-launch={0}x{1}".format(self.config["NV"]["THREADS"],self.config["NV"]["BLOCKS"])],bufsize=1024,cwd=self.cwd+'\\miners\\XMR\\XMRIG\\win\\',universal_newlines=True,shell=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
            self.log.info("NV Miner Started.")
    
    def stopNV(self):
        try:
            self.nv.kill()
            self.log_nv.close()
            self.log.info("NV Miner Stopped.")  
        except: 
            pass
        
    def quit(self):
        try:
            self.stopCPU()
        except: pass
        try:
            self.stopNV()
        except: pass
        try:
            self.stopAMD()
        except: pass
        self.exec = False
        
    def run(self):
        self.log.info("Start Mining XMR/Monero with XMRIG on {0}".format(self.pt))
        while (self.exec is True):
            ''' Keep Miners busy: '''
            '''CPU:'''
            if (self.config["CPU"]["ENABLE"] is True):
                    if (self.exec_cpu == True):
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
                            self.log.info("Stopping CPU Miner")
            '''NVIDIA:'''
            if (self.config["NV"]["ENABLE"] is True):
                    if (self.exec_nv == True):
                        if (self.nv == False):
                            self.startNV()
                        else:
                            if (self.nv.poll() != None):
                                self.log.warning("NV Miner has exited; restart...")
                                self.startNV()
                    else:

                        if (self.nv != False):
                            self.nv.kill()
                            self.nv = False
                            self.log.info("Stopping NV Miner")
            '''AMD:'''
            if (self.config["AMD"]["ENABLE"] is True):
                    if (self.exec_amd == True):
                        if (self.amd == False):
                            self.startAMD()
                        ###else:
                            if (self.amd.poll() != None):
                                self.log.warning("AMD Miner has exited; restart...")
                                self.startAMD()
                    else:

                        if (self.amd != False):
                            self.amd.kill()
                            self.amd = False
                            self.log.info("Stopping AMD Miner")
            ''' Process outputs: '''

            self.processOutput()
            time.sleep(10)
