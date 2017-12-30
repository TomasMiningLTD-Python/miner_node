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
            fp = open(self.cwd+"/"+self.config["GLOBAL"]["configskel"],"r")
            if (platform.system()=="Linux"):
                self.pt = "linux"
            elif (platform.system()=="Windows"):
                self.pt = "win"
            self.init_cfg = json.loads(fp.read(-1))
            self._pools()
        except Exception as e:
            print("Unable to load config skeleton: {0}/{1}".format(self.cwd,self.config["GLOBAL"]["configskel"]))
            print(e)
            sys.exit()
                
    def _pools(self):
    
        if (self.config["POOLS"]["url0"] != ""):
            cfg = {'url':self.config["POOLS"]["url0"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url2"] != ""):
            cfg = {'url':self.config["POOLS"]["url2"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url1"] != ""):
            cfg = {'url':self.config["POOLS"]["url1"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url3"] != ""):
            cfg = {'url':self.config["POOLS"]["url3"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url4"] != ""):
            cfg = {'url':self.config["POOLS"]["url4"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url5"] != ""):
            cfg = {'url':self.config["POOLS"]["url5"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url6"] != ""):
            cfg = {'url':self.config["POOLS"]["url6"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url7"] != ""):
            cfg = {'url':self.config["POOLS"]["url7"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url8"] != ""):
            cfg = {'url':self.config["POOLS"]["url8"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)
        if (self.config["POOLS"]["url9"] != ""):
            cfg = {'url':self.config["POOLS"]["url9"],'user':self.config["POOLS"]["payment"],'pass':self.config["POOLS"]["minerName"],'keepalive':'true','nicehash':'false'}
            self.init_cfg["pools"].append(cfg)

                
    def mkCPU(self):
        #try:
        cfg = self.init_cfg
        #cfg["background"] = True
        cfg["threads"] = self.config["CPU"]["threads"]
        cfg["max-cpu-usage"] = self.config["CPU"]["max"]
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["CPU"]["log"]
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["CPU"]["log"] 
        cfile = open(self.cwd+"/bin/{0}/".format(self.pt)+self.config["CPU"]["config"],"wt")
        cfile.write(json.dumps(cfg))
        cfile.close()
 
    def mkNV(self):
        #try:
        cfg = self.init_cfg
        cfg["threads"] = {"threads":self.config["NVIDIA"]["threads"],"blocks":self.config["NVIDIA"]["blocks"],"bfactor":self.config["NVIDIA"]["bfactor"],"bsleep":self.config["NVIDIA"]["bsleep"]}
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["NVIDIA"]["log"]
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["NVIDIA"]["log"] 
        
        cfile = open(self.cwd+"/bin/{0}/".format(self.pt)+self.config["NVIDIA"]["config"],"wt")
        cfile.write(json.dumps(cfg))
        cfile.close()

    def mkAMD(self):
        #try:
        cfg = self.init_cfg
        cfg["threads"] = {}
        if (self.pt == "linux"):
            cfg["log-file"] = self.cwd+"/log/"+self.config["AMD"]["log"]
        elif (self.pt == "win"):
            cfg["log-file"] = self.cwd+"\\log\\"+self.config["AMD"]["log"] 
        
        cfile = open(self.cwd+"/bin/{0}/".format(self.pt)+self.config["AMD"]["config"],"wt")
        cfile.write(json.dumps(cfg))
        cfile.close()
