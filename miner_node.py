#!/usr/bin/python3
'''
Documentation, License etc.

@package miner_node
'''

import sys,getopt,argparse
from configparser import ConfigParser

from daemon import MinerDaemon
from network.daemon import NetworkDaemon
from multiprocessing import Pipe
import platform
if __name__ == '__main__':
    configp = False
    parser = argparse.ArgumentParser(description="Manage Mining Node")
    parser.add_argument('-c', '--config')
    parser.add_argument('-v', dest='verbose', action='store_true')
    args = parser.parse_args()
    if 'config' not in args:
        print('Config File not found.')
        print ('miner_node.py -c config_file')
        sys.exit()
    try:
        config = ConfigParser()
        config.read(args.config)
    except Exception as e:
        print ('Invaid Config file!!!')
        print(e)
        sys.exit()


dpi,npi = Pipe()
daemon = MinerDaemon()
daemon.setup(config,dpi)
daemon.start()
network = NetworkDaemon()
network.setup({"miner_id":1,"remote":{"api_endpoint":config["GLOBAL"]["endpoint"]}},npi,dpi)
network.enabled = True
network.start()
network.join()

