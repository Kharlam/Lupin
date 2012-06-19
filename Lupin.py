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
    print "Options (See Readme for complete details):"
    print "-h --help\n\t\tPrint this help message.\n"
    print "-l <port>, --listen=<port>\n\t\tPort to listen on [default 10000]\n"
    print "-t <target_list>, --targets=<target_list>\n\t\tList of target sites [default \"target_list.txt\"]\n"
    print "-b <seconds>, --burst=<seconds>\n\t\tLength of attack burst [default 2]\n"    
    print "-s <seconds>, --sleep=<seconds>\n\t\tTime between attack bursts [default 15]\n"
    print "-f, --focus\n\t\tRun attack while tab is in focus\n"
    print "-n --nibble\n\t\tSingle burst as soon as page gets loads\n"
    print "--bold\n\t\tGreatly increases speed at the cost of stealth.\n"
    print ""

def parseOptions(argv):
    targetsFile			= "target_list.txt"
    port				= 10000
    burstDuration       = 2
    sleepDuration     	= 15    
    runWhileInFocus   	= "false"
    nibble			  	= "false"
    bold          		= False
    
    
    try:                                
        opts, args = getopt.getopt(argv, "t:p:b:s:fnh", 
                                   ["targets=","port=","burst=","sleep=","focus","nibble","bold","help"])
        for opt, arg in opts:

            if opt in ("-t", "--targets"):
                targetsFile = arg	
            elif opt in ("-p", "--port"):
                port = int(arg)
            elif opt in ("-b", "--burst"):
                burstDuration = int(arg)     
            elif opt in ("-s", "--sleep"):
                sleepDuration = int(arg)            
            elif opt in ("-f", "--focus"):
                runWhileInFocus = "true"	
            elif opt in ("-n","--nibble"):
                nibble = "true"
            elif opt in ("--bold"):
                bold = True
            elif opt in ("-h", "--help"):
                usage()
                sys.exit()
			                    
        return (targetsFile, port, burstDuration, sleepDuration, runWhileInFocus, nibble ,bold)
                    
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                         

def main(argv):
    (targetsFile, port, burstDuration, sleepDuration, runWhileInFocus, nibble, bold) = parseOptions(argv)

    try:
        targets_fd = open(targetsFile)
    except:
        print sys.exc_info()[0]
        usage()
        sys.exit()

    try:
        if sleepDuration < 0 or burstDuration < 0:
            usage()
            sys.exit()  
    except:
        usage()
        sys.exit()
        
    obfuscateTargets = "true"
    
    if runWhileInFocus == "true":
        nibble = "false"
        
	
    if bold:
        runWhileInFocus = "true"
        nibble = "false"
        sleepDuration = 0
        burstDuration = 100
        obfuscateTargets = "false"
		
    p = PersistentData.getInstance()
    p.setLoginActions(targets_fd)
    
    p.setMasterIframeVars(sleepDuration*1000, burstDuration*1000, targets_fd, runWhileInFocus, nibble, obfuscateTargets)
    
    LupinFactory              = http.HTTPFactory(timeout=10)
    LupinFactory.protocol     = LupinProxy

    reactor.listenTCP(port, LupinFactory)           
    print "\nLupin by Raul Gonzalez running...\n"
	
    if bold:
        print "Stealth Measures Disabled! See Readme for more details.\n"
    reactor.run()

if __name__ == '__main__':
    main(sys.argv[1:])
