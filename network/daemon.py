import requests
import json
import time
import datetime
import sys,getopt
import datetime
import threading
import platform
import logging
import netifaces
from . import methods
logging.basicConfig(level=logging.INFO)
class NetworkDaemon(threading.Thread):
    macaddr = False
    config = False
    auth = False
    pipe_in = False
    pipe_out = False
    csrf = False
    log = logging.getLogger("Network")
    enabled = False
    cmd_enabled = False
    cfg_enabled = False
    started = False
    def setup(self,config,pipe_out,pipe_in):
        
        self.config = config
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.macaddr = netifaces.ifaddresses(netifaces.interfaces()[self.config["miner_id"]])[netifaces.AF_LINK][0]['addr']
        self.log.info("Network IO Configuration: endpoint: {1}, node: {0}".format(self.macaddr,self.config["remote"]["api_endpoint"]))
        
    def _geturl(self,url,params):
        self.log.info("GET url: {0}".format(self.config["remote"]["api_endpoint"]+url))
        try:
            r = requests.get(self.config["remote"]["api_endpoint"]+url,params)
            if (r.status_code == 500):
                self.log.error("PROTOCOL ERROR [500]: {0}".format(r.url))
                return False
            if (r.status_code == 404):
                self.log.error("PROTOCOL ERROR [404]: {0}".format(r.url))
                return False
            if (r.status_code == 200):
                #print(r.cookies)
                if ('csrftoken' in r.cookies):
                    self.csrf = r.cookies['csrftoken']
                    
                try:
                    payload = r.json()
                    return payload
                except:
                    self.log.error("PROTOCOL ERROR: DATA IS NOT JSON: {0}".format(r.url))
                    return False
        except Exception as e:
            self.log.error("Request Error for url {0}: {1}".format(self.config["remote"]["api_endpoint"]+url,e))
            self.pipe_out.send({'type':'err','err':'CONN-REFUSED'})
            return False    

    
    def _posturl(self,url,params):
        self.log.info("POST to url: {0}".format(self.config["remote"]["api_endpoint"]+url))
        hdr = {'csrftoken':self.csrf}
        #print(hdr)
        params["csrfmiddlewaretoken"] = self.csrf
        params["miner_id"]= self.macaddr
        #print(params)
        try:
            r = requests.post(self.config["remote"]["api_endpoint"]+url,data=params,cookies=hdr)
            if (r.status_code == 500):
                self.log.error("PROTOCOL ERROR [500]: {0}".format(r.url))
                return False
            if (r.status_code == 404):
                self.log.error("PROTOCOL ERROR [404]: {0}".format(r.url))
                return False
            if (r.status_code == 200):
                try:
                    payload = r.json()
                    return payload
                except:
                    self.log.error("PROTOCOL ERROR: DATA IS NOT JSON: {0}".format(r.url))
                    return False
        except Exception as e:
            self.log.error("Request Error for url {0}: {1}".format(self.config["remote"]["api_endpoint"]+url,e))
            return False    
        return True

    
    def auth_request(self):
        self.log.info("Authenticating to Endpoint, node: {0}".format(self.macaddr))
        localtime = datetime.datetime.now()
        self.pipe_out.send({"type":"status","msg":"NET-STOP"})
        r = self._geturl(methods.AUTH,{'id':self.macaddr,'time':localtime})
        if (r is not False):
            if (r["result"] == "noauth"):
                self.log.warn("Node is not authenticated. Waiting for account ownership. Sleeping for 30 seconds.")
                self.pipe_out.send({"type":"err","msg":"AUTH-ERR"})
                time.sleep(20)
            elif (r["result"] == "auth-ok"):
                self.log.info("Authentication Success!")
                self.auth = True
                self.pipe_out.send({'type':'status','msg':'AUTH-OK'})
                
                
    def stop(self):
        self.enabled = False
        self.auth = False
        self.log.info("Stop Network Activity.")
        
    def quit(self):
        self.exit = True
        
    def run(self):
            self.started = True
            self.exit = False
            while(self.exit is not True):
                if (self.enabled is True):
                    """If we're not authorised, go to that routine only."""
                    if self.auth is False:
                        self.auth_request()
                    else:
                        " We are authorised, lets do some damage: "
                        while (self.pipe_in.poll() > 0):
                            """ We have something to send to the server, lets do it."""
                            msg = self.pipe_in.recv()
                            if ('method' not in msg):
                                self.log.warn("MSG in queue, does not have METHOD. Not sending. {0}".format(msg))
                            else:
                                try:
                                    self._posturl(getattr(methods,msg["method"]),msg["payload"])
                                except Exception as e:
                                    self.log.error("ERROR DURING POST: {e}".format(e))
                                    print(e)
                time.sleep(10)

                
        
        
        
