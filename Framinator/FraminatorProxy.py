

from twisted.web.http import HTTPChannel
from ClientRequest import ClientRequest

class FraminatorProxy(HTTPChannel):
    requestFactory = ClientRequest
