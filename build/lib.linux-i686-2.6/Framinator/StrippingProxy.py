

from twisted.web.http import HTTPChannel
from ClientRequest import ClientRequest

class StrippingProxy(HTTPChannel):
    requestFactory = ClientRequest
