import logging
logging.basicConfig(level=logging.INFO)
class MinerParser():
    log = logging.getLogger('miner_stats')
    total = [0,0,0]
    highest = [0,0,0]
    cpu = [0,0,0,0,0,0,0,0,0,0]
    nv = [0,0,0,0,0,0,0,0,0,0,0,0]
    amd = [0,0,0,0,0,0,0,0,0,0,0,0]
    ''' Strip the date of any incoming string: '''
    def _stripString(self,string):
        try:
            return string[22:]
        except:
            return False
    ''' Parse Harshrate:'''
    def _hashRate(self,string):
        try:
            rate    = string[18:].split(' ')
            
        except:
            return False
        rr = False
        try:
            if (rate[2] != 'n/a'):
                rr= rate[2]
            if (rate[1] != 'n/a'):
                rr= rate[1]
            if (rate[0] != 'n/a'):
                rr= rate[0]        
            if (rate[5] != 'n/a'):
                mr = rate[5]
            else:
                mr = 0
            if rr is not False:
                return [rr,mr]
            else:
                return False
        except:
            return False
    ''' Parse Accepted: '''
    def _accepted(self,string):
        try:
            acc = string[9:].split(" ")
        except:
            return False
        return ([acc[0],acc[2]])
    ''' Parse new Job/Pool: '''
    def _pool(self,string):
        try:
            pool = string.split(" ")
        except:
            return False
        return pool[3]
    
    def parseCPU(self,istr):
        if (istr == ''):
            return True
        string = self._stripString(istr)
        if (string is False): return False
        
        if (string[3:15] == "HUGE PAGES: "):
            stt = string.split(":   ")
            
            if (stt[1][-8:-1] != "enabled"):
                self.log.info("Huge Page Support enabled!")
                return False
            else:
                self.log.warn("Huge Page Support is not enabled!")
                return {"warn":"cpu","value":"huge-page"}
                

        if (string[3:17] == "CPU:          "):
            stt = string.split(":          ")
            self.log.info("CPU Type: {0}".format(stt[1][:-1]))
            return {"type":"cpu","value":stt[1][:-1]}
        if (string == "no active pools, stop mining"):
            self.log.warn("[CPU] No active pools detected.")
            return False
        if (string[0:5] == 'speed'):
            try:
                rate = self._hashRate(string[1:])
                if (rate is not False):
                    self.log.info("[CPU] Speed: {0} H/s, Highest: {1} H/s".format(rate[0],rate[1]))
                    self.total[0] = float(rate[0])
                    self.highest[0] = float(rate[1])
                else:
                    self.total[0] = 0
                    self.highest[0] = 0
                self.cpu[0] = self.total[0]
                return False
            except: return False
        if (string[0:8] == 'accepted'):
                acc = self._accepted(string)
                self.log.info("[CPU] Accepted: {0} Shares at difficulty: {1}".format(acc[0],acc[1]))
                return False
        if (string[0:3] == 'new'):
                pool = self._pool(string)
                self.log.info("[CPU] New Job from Pool: {0}".format(pool))
                return False
            
    def parseNV(self,istr):
        if (istr == ''):
            return True
        string = self._stripString(istr)
        if (string is False): return False
    
        if (string == "no active pools, stop mining"):
            self.log.warn("[NV] No active pools detected.")
            return True
        try:
            if (string[0:5] == 'speed'):
                rate = self._hashRate(string)
                if (rate is not False):
                    self.log.info("[NV] Speed: {0} H/s Highest {1} H/s".format(rate[0],rate[1]))
                    self.total[1] = float(rate[0])
                    self.highest[1] = float(rate[1])
                    #return True
                else:
                    self.total[1] = 0
                    self.highest[1] = 0
                    self.nv[0] = self.total[1]
                    return False
        except: return False
        if (string[0:8] == 'accepted'):
                acc = self._accepted(string)
                self.log.info("[NV] Accepted: {0} Shares at difficulty: {1}".format(acc[0],acc[1]))
                return True
        if (string[0:3] == 'new'):
                pool = self._pool(string)
                self.log.info("[NV] New Job from Pool: {0}".format(pool))
                return True
    def parseAMD(self,istr):
        if (istr == ''):
            return True
        string = self._stripString(istr)
        if (string is False): return False
    
        if (string == "no active pools, stop mining"):
            self.log.warn("[AMD] No active pools detected.")
            return True
        try:
            if (string[0:5] == 'speed'):
                rate = self._hashRate(string)
                if (rate[0] is not False):
                    self.log.info("[AMD] Speed: {0} H/s Highest {1} H/s".format(rate[0],rate[1]))
                    self.total[2] = float(rate[0])
                    self.highest[2] = float(rate[1])
                    #return True
                else:
                    self.total[2] = 0
                    self.highest[2] = 0
                self.amd[0] = self.total[2]
                return False
        except: return False
        if (string[0:8] == 'accepted'):
                acc = self._accepted(string)
                self.log.info("[AMD] Accepted: {0} Shares at difficulty: {1}".format(acc[0],acc[1]))
                return True
        if (string[0:3] == 'new'):
                pool = self._pool(string)
                self.log.info("[AMD] New Job from Pool: {0}".format(pool))
                return True

    def reset(self):
        self.total = [0,0,0]
        self.highest = [0,0,0]
        
    def getSpeed(self):
        cpu = str(self.cpu[0])+","+str(self.cpu[1])+","+str(self.cpu[3])+","+str(self.cpu[4])+","+str(self.cpu[5])+","+str(self.cpu[6])+","+str(self.cpu[7])+","+str(self.cpu[8])+","+str(self.cpu[9])
        nv = str(self.nv[0])+","+str(self.nv[1])+","+str(self.nv[3])+","+str(self.nv[4])+","+str(self.nv[5])+","+str(self.nv[6])+","+str(self.nv[7])+","+str(self.nv[8])+","+str(self.nv[9])+","+str(self.nv[10])+","+str(self.nv[11])
        amd = str(self.amd[0])+","+str(self.amd[1])+","+str(self.amd[3])+","+str(self.amd[4])+","+str(self.amd[5])+","+str(self.amd[6])+","+str(self.amd[7])+","+str(self.amd[8])+","+str(self.amd[9])+","+str(self.amd[10])+","+str(self.amd[11])
        return {'cpu':cpu,'nv':nv,'amd':amd}
    
    def getTotal(self):
        gt = self.total[0]+self.total[1]+self.total[2]
        ht = self.highest[0]+self.highest[1]+self.highest[2]
        if (gt > 0.1):
            self.log.info("Current Total speed: {0} H/s. Highest: {1} H/s".format(gt,ht))
        return {'t':gt,'h':ht,'c':self.total[0],'n':self.total[1],'a':self.total[2]}

