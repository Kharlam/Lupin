from twisted.internet.protocol import ClientFactory

class ServerConnectionFactory(ClientFactory):

    def __init__(self, command, uri, postData, actAs ,headers, client):
        self.command      = command
        self.uri          = uri
        self.postData     = postData
        self.headers      = headers
        self.client       = client
        self.actAs        = actAs

    def buildProtocol(self, addr):
        return self.protocol(self.command, self.uri, self.postData, self.actAs,self.headers, self.client)
    
    def clientConnectionFailed(self, connector, reason):
        self.client.finish()

