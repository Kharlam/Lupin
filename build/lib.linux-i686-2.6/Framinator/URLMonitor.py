

import re

class URLMonitor:    

    '''
    The URL monitor maintains a set of (client, url) tuples that correspond to requests which the
    server is expecting over SSL.  
    '''

    # Start the arms race, and end up here...
    javascriptTrickery = [re.compile("http://.+\.etrade\.com/javascript/omntr/tc_targeting\.html")]
    _instance          = None

    def __init__(self):
        self.strippedURLPorts   = {}

    def isSecureLink(self, client, url):
        for expression in URLMonitor.javascriptTrickery:
            if (re.match(expression, url)):
                return True

        return False

    
  
    def getInstance():
        if URLMonitor._instance == None:
            URLMonitor._instance = URLMonitor()

        return URLMonitor._instance
    
    getInstance = staticmethod(getInstance)
