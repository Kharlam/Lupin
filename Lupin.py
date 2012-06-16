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
    print "-h --help\n\t\tPrint this help message.\n"
    print "-l <port>, --listen=<port>\n\t\tPort to listen on [default 10000]\n"
    print "-t <target_list>, --targets=<target_list>\n\t\tList of target sites [default \"target_list.txt\"]\n"
    print "-s <seconds>, --sleep=<seconds>\n\t\tTime between attack bursts [default 20]\n"
    print "-f, --focus\n\t\tRun attack while tab is in focus\n"
    print "-n --nibble\n\t\tBurst as soon as the page gets loaded\n"
    print "-b --bold\n\t\tSets 'sleep=0', and 'focus' flags\n"
    print ""

def parseOptions(argv):
    targetsFile			= "target_list.txt"
    port				= 10000
    sleepDuration     	= 20
    runWhileInFocus   	= "false"
    nibble			  	= "false"
    bold          		= False
    
    try:                                
        opts, args = getopt.getopt(argv, "t:p:s:fnbh", 
                                   ["targets=","port=","sleep=","focus","nibble","bold","help"])
        for opt, arg in opts:

            if opt in ("-t", "--targets"):
                targetsFile = arg	
            elif opt in ("-p", "--port"):
                port = int(arg)
            elif opt in ("-s", "--sleep"):
                sleepDuration = int(arg)
            elif opt in ("-f", "--focus"):
                runWhileInFocus = "true"	
            elif opt in ("-n","--nibble"):
                nibble = "true"
            elif opt in ("-b","--bold"):
                bold = True
            elif opt in ("-h", "--help"):
                usage()
                sys.exit()
			                    
        return (port, sleepDuration, runWhileInFocus, targetsFile, nibble ,bold)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (port, sleepDuration, runWhileInFocus, targetsFile, nibble, bold) = parseOptions(argv)

    try:
        targets_fd = open(targetsFile)
    except:
        print sys.exc_info()[0]
        usage()
        sys.exit()

    try:
        if sleepDuration < 0:
            sleepDuration = 0
    except:
        usage()
        sys.exit()
        
    obfuscateTargets = "true"
	
    if bold:
        runWhileInFocus = "true"
        sleepDuration = 0
        obfuscateTargets = "false"
		
    p = PersistentData.getInstance()
    p.setLoginActions(targets_fd)
    
	
    
    p.setMasterIframeVars(sleepDuration*1000, targets_fd, runWhileInFocus, nibble, obfuscateTargets)
    
    LupinFactory              = http.HTTPFactory(timeout=10)
    LupinFactory.protocol     = LupinProxy

    reactor.listenTCP(port, LupinFactory)           
    print "\nLupin by Raul Gonzalez running...\n"
	
    if bold:
        print "Bold Mode Activated - Stealth Lost. See Readme for more details."
    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
