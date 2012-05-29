#!/usr/bin/env python

 
__author__ = "Raul Gonzalez"


from twisted.web import http
from twisted.internet import reactor

from Lupin.URLMonitor import URLMonitor
from Lupin.LupinProxy import LupinProxy

import sys, getopt, logging, traceback, string, os

def usage():
    print "\nLupin " + gVersion + " by Raul Gonzalez"
    print "Usage: Lupin <options>\n"
    print "Options:"
    print "-w <filename>, --write=<filename> Specify file to log to (optional)."
    print "-l <port>, --listen=<port>        Port to listen on (default 10000)."
    print "-k , --killsessions               Kill sessions in progress."
    print "-h                                Print this help message."
    print ""

def parseOptions(argv):
    logFile      = 'Lupin.log'
    logLevel     = logging.WARNING
    listenPort   = 10000
    killSessions = False
    maxTargets	 = 20000
    
    try:                                
        opts, args = getopt.getopt(argv, "hw:l:psafk", 
                                   ["help", "write=","targets=","listen=","killsessions"])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-w", "--write"):
                logFile = arg 
            elif opt in ("-t", "--targets"):
                maxTargets = arg 
            elif opt in ("-l", "--listen"):
                listenPort = arg
            elif opt in ("-k", "--killsessions"):
                killSessions = True

        return (logFile, logLevel, listenPort, killSessions,maxTargets)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (logFile, logLevel, listenPort, killSessions,maxTargets) = parseOptions(argv)
        
    logging.basicConfig(level=logLevel, format='%(asctime)s %(message)s',filename=logFile, filemode='w')

    LupinFactory              = http.HTTPFactory(timeout=10)
    LupinFactory.protocol     = LupinProxy

    reactor.listenTCP(int(listenPort), LupinFactory)
                
    print "\nLupin by Raul Gonzalez running..."

    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
