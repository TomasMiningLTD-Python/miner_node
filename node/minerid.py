import netifaces
class minerID():
    ifaces = False
    ifaceids = False
    def __init__(self):
        self.ifaces = netifaces.interfaces()
        self.ifaceids = {}
        for i in self.ifaces:
            try:
                self.ifaceids[i] = netifaces.ifaddresses(i)[netifaces.AF_LINK][0]['addr']
            except: pass

