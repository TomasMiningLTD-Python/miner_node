import json,os
class MinerConfig():
    config = False
    path = False
    locked = False
    
    
    def save(self,path=False):
        if (path is False):
            if self.path == False: return False
            config = open(self.path,"tw")
        else:
            config = open(path,"tw")     
        config.write(json.dumps(self.config))
        return True
                
    def load(self,path):
        if (path == None):
            path = os.getcwd()+"/node/miner_cfg.json"
            config = open(path)
        elif (path != None):
            config = open(path)
            self.path = path
        elif (self.path != False):
            self.path = path
            config = open(self.path)
        try:
            self.config = json.loads(config.read())
            config.close()
        except: raise Exception('Invalid Config File')
        print("Loaded config {0}".format(path))
        print(self.config)
        
 
