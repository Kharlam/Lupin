from twisted.web.http import HTTPChannel
from ClientRequest import ClientRequest

class LupinProxy(HTTPChannel):
    requestFactory = ClientRequest
