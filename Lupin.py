#!/usr/bin/env python
 
__author__ = "Raul Gonzalez"

from twisted.web import http
from twisted.internet import reactor
from Lupin.LupinProxy import LupinProxy
from Lupin.PersistentData import PersistentData

import sys, getopt, logging, traceback, string, os

def usage():
    print "\nLupin by Raul Gonzalez"
    print "Usage: Lupin <options>\n"
    print "Options:"
    print "-l <port>, --listen=<port>                     Port to listen on (default 10000)."
    print "-s <seconds>, --sleep=<seconds>                Time between attack sessions in seconds (default 20)."
    print "-r <seconds>, --refresh=<seconds>              Length of attack session in Seconds (default 2)."
    print "-h                                             Print this help message."
    print ""

def parseOptions(argv):
    listenPort        = 10000
    sleepInterval     = 10
    limitRefresh      = 3

    
    try:                                
        opts, args = getopt.getopt(argv, "hw:l:psafk", 
                                   ["help","listen=","sleep=","refresh="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-l", "--listen"):
                listenPort = arg
	    elif opt in ("-s", "--sleep"):
		if arg >= 0:
                    sleepInterval = arg
	    elif opt in ("-r", "--refresh"):
		if arg >= 0:
                    limitRefresh = arg
         
           
        return (listenPort, sleepInterval, limitRefresh)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (listenPort, sleepInterval, limitRefresh) = parseOptions(argv)

    
    PersistentData.getInstance().setSlaveVariables(limitRefresh*50, sleepInterval*1000)
    
    LupinFactory              = http.HTTPFactory(timeout=10)
    LupinFactory.protocol     = LupinProxy

    reactor.listenTCP(int(listenPort), LupinFactory)           
    print "\nLupin by Raul Gonzalez running..."
    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
