import sys,os,json,platform
class MinerCFG():
    config = False
    skel = False
    init_cfg = False
    cwd = False
    pt = False
    def __init__(self,config):
        self.config = config
        try:
            self.cwd = os.getcwd()
            fp = open(self.cwd+"/miners/XMR/XMRIG/config.skel","r")
            if (platform.system()=="Linux"):
                self.pt = "linux"
            elif (platform.system()=="Windows"):
                self.pt = "win"
            self.init_cfg = json.loads(fp.read(-1))
            self._pools()
        except Exception as e:
            print("Unable to load config skeleton: {0}/{1}".format(self.cwd,"/miners/XMR/XMRIG/config.skel"))
            print(e)
            sys.exit()
                
    def _pools(self):
    
        if (self.config["URL0"] != ""):
            cfg = {'url':self.config["URL0"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL2"] != ""):
            cfg = {'url':self.config["URL2"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL1"] != ""):
            cfg = {'url':self.config["URL1"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL3"] != ""):
            cfg = {'url':self.config["URL3"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL4"] != ""):
            cfg = {'url':self.config["URL4"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL5"] != ""):
            cfg = {'url':self.config["URL5"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL6"] != ""):
            cfg = {'url':self.config["URL6"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL7"] != ""):
            cfg = {'url':self.config["URL7"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL8"] != ""):
            cfg = {'url':self.config["URL8"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["URL9"] != ""):
            cfg = {'url':self.config["URL9"],'user':self.config["PAYMENT_ADDR"],'pass':self.config["PASSWORD"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)

                
    def mkCPU(self):
        #try:
        cfg = self.init_cfg
        #cfg["background"] = True
        cfg["threads"] = self.config["CPU"]["THREADS"]
        cfg["max-cpu-usage"] = self.config["CPU"]["MAX"]
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["CPU"]["LOG"]
            cfile = open(self.cwd+"/tmp/cpu.json","wt")
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["CPU"]["LOG"] 
            cfile = open(self.cwd+"\\tmp\\cpu.json","wt")
        cfile.write(json.dumps(cfg))
        cfile.close()
 
    def mkNV(self):
        #try:
        cfg = self.init_cfg
        cfg["threads"] = {"THREADS":self.config["NV"]["THREADS"],"blocks":self.config["NV"]["BLOCKS"],"bfactor":self.config["NV"]["BFACTOR"],"bsleep":self.config["NV"]["BSLEEP"]}
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["NV"]["LOG"]
            cfile = open(self.cwd+"/tmp/nv.json","wt")
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["NV"]["LOG"] 
            cfile = open(self.cwd+"\\tmp\\nv.json","wt")
        

        cfile.write(json.dumps(cfg))
        cfile.close()

    def mkAMD(self):
        #try:
        cfg = self.init_cfg
        cfg["threads"] = {}
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["AMD"]["LOG"]
            cfile = open(self.cwd+"/tmp/amd.json","wt")
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["AMD"]["LOG"]
            cfile = open(self.cwd+"\\tmp\\amd.json","wt")
        
        
        cfile.write(json.dumps(cfg))
        cfile.close()
