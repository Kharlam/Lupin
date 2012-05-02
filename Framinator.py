#!/usr/bin/env python

 
__author__ = "Raul Gonzalez"
__email__  = "graulito@hushmail.com"


from twisted.web import http
from twisted.internet import reactor

from Framinator.StrippingProxy import StrippingProxy
from Framinator.URLMonitor import URLMonitor
from Framinator.CookieCleaner import CookieCleaner

import sys, getopt, logging, traceback, string, os

gVersion = "0.1"

def usage():
    print "\nFraminator " + gVersion + " by Raul Gonzalez"
    print "Usage: Framinator <options>\n"
    print "Options:"
    print "-w <filename>, --write=<filename> Specify file to log to (optional)."
    print "-p , --post                       Log only SSL POSTs. (default)"
    print "-s , --ssl                        Log all SSL traffic to and from server."
    print "-a , --all                        Log all SSL and HTTP traffic to and from server."
    print "-l <port>, --listen=<port>        Port to listen on (default 10000)."
    print "-k , --killsessions               Kill sessions in progress."
    print "-h                                Print this help message."
    print ""

def parseOptions(argv):
    logFile      = 'Framinator.log'
    logLevel     = logging.WARNING
    listenPort   = 10000
    killSessions = False
    
    try:                                
        opts, args = getopt.getopt(argv, "hw:l:psafk", 
                                   ["help", "write=", "post", "ssl", "all", "listen=","killsessions"])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-w", "--write"):
                logFile = arg
            elif opt in ("-p", "--post"):
                logLevel = logging.WARNING
            elif opt in ("-s", "--ssl"):
                logLevel = logging.INFO
            elif opt in ("-a", "--all"):
                logLevel = logging.DEBUG
            elif opt in ("-l", "--listen"):
                listenPort = arg
            elif opt in ("-k", "--killsessions"):
                killSessions = True

        return (logFile, logLevel, listenPort, killSessions)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (logFile, logLevel, listenPort, killSessions) = parseOptions(argv)
        
    logging.basicConfig(level=logLevel, format='%(asctime)s %(message)s',filename=logFile, filemode='w')

    CookieCleaner.getInstance().setEnabled(killSessions)

    strippingFactory              = http.HTTPFactory(timeout=10)
    strippingFactory.protocol     = StrippingProxy

    reactor.listenTCP(int(listenPort), strippingFactory)
                
    print "\nFraminator " + gVersion + " by Raul Gonzalez running..."

    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
