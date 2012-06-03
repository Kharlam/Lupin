#!/usr/bin/env python

 
__author__ = "Raul Gonzalez"

from twisted.web import http
from twisted.internet import reactor
from Lupin.LupinProxy import LupinProxy
import sys, getopt, logging, traceback, string, os

def usage():
    print "\nLupin by Raul Gonzalez"
    print "Usage: Lupin <options>\n"
    print "Options:"
    print "-l <port>, --listen=<port>        Port to listen on (default 10000)."
    print "-k , --killsessions               Kill sessions in progress."
    print "-h                                Print this help message."
    print ""

def parseOptions(argv):
    listenPort   = 10000
    killSessions = False
    maxTargets	 = 20000
    
    try:                                
        opts, args = getopt.getopt(argv, "hw:l:psafk", 
                                   ["help", "targets=","listen=","killsessions"])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-t", "--targets"):
                maxTargets = arg 
            elif opt in ("-l", "--listen"):
                listenPort = arg
            elif opt in ("-k", "--killsessions"):
                killSessions = True

        return (listenPort, killSessions,maxTargets)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (listenPort, killSessions,maxTargets) = parseOptions(argv)
    LupinFactory              = http.HTTPFactory(timeout=10)
    LupinFactory.protocol     = LupinProxy
    reactor.listenTCP(int(listenPort), LupinFactory)           
    print "\nLupin by Raul Gonzalez running..."
    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
