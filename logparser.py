import logging
logging.basicConfig(level=logging.INFO)
class MinerParser():
    log = logging.getLogger('miner_stats')
    total = [0,0,0]
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
        if (rate[2] != 'n/a'):
            return rate[2]
        if (rate[1] != 'n/a'):
            return rate[1]
        if (rate[0] != 'n/a'):
            return rate[0]        
        return 'n/a'
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
        if (string[3:7] == "CPU:"):
            stt = string.split(":          ")
            self.log.info("CPU Type: {0}".format(stt[1]))
        if (string == "no active pools, stop mining"):
            self.log.warn("[CPU] No active pools detected.")
            return True
        if (string[0:5] == 'speed'):
            rate = self._hashRate(string[1:])
            if (rate is not False):
                self.log.info("[CPU] Speed: {0} H/s".format(rate))
                self.total[0] = float(rate)
                return True
            else:
                self.total[0] = 0
                return False
        if (string[0:8] == 'accepted'):
                acc = self._accepted(string)
                self.log.info("[CPU] Accepted: {0} Shares at difficulty: {1}".format(acc[0],acc[1]))
                return True
        if (string[0:3] == 'new'):
                pool = self._pool(string)
                self.log.info("[CPU] New Job from Pool: {0}".format(pool))
                return True
            
    def parseNV(self,istr):
        if (istr == ''):
            return True
        string = self._stripString(istr)
        if (string is False): return False
    
        if (string == "no active pools, stop mining"):
            self.log.warn("[NV] No active pools detected.")
            return True
        if (string[0:5] == 'speed'):
            rate = self._hashRate(string)
            if (rate is not False):
                self.log.info("[NV] Speed: {0} H/s".format(rate))
                self.total[1] = float(rate)
                return True
            else:
                self.total[0] = 0
                return False
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
        if (string[0:5] == 'speed'):
            rate = self._hashRate(string)
            if (rate is not False):
                self.log.info("[AMD] Speed: {0} H/s".format(rate))
                self.total[2] = float(rate)
                return True
            else:
                self.total[0] = 0
                return False
        if (string[0:8] == 'accepted'):
                acc = self._accepted(string)
                self.log.info("[AMD] Accepted: {0} Shares at difficulty: {1}".format(acc[0],acc[1]))
                return True
        if (string[0:3] == 'new'):
                pool = self._pool(string)
                self.log.info("[AMD] New Job from Pool: {0}".format(pool))
                return True
            
    def getTotal(self):
        self.log.info("Current Total speed: {0} H/s".format(self.total[0]+self.total[1]+self.total[2]))
