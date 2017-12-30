#!/usr/bin/python3
'''
Documentation, License etc.

@package miner_node
'''

import sys,getopt,argparse
from configparser import ConfigParser

from daemon import MinerDaemon

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


daemon = MinerDaemon()
daemon.setup(config)
daemon.start()
