import time
from subsystem import subsystem

class memcache(subsystem):
    actions = "clear"

    def __init__(self, MCP_dir):
        subsystem.__init__(self, MCP_dir)
        self.state = { 'resource':self.__class__.__name__,
                       'date':time.strftime("%Y-%m-%d %H:%M:%S")
                     }
        self.memhost = self.parser.get('memcache', 'memhost')

    def clear(self):
        print "Clearing memcache:"
        sout, serr = self.run_cmd(self.MCP_dir + "bin/clear_memcache.pl " + self.memhost)
        print "memcache cleared!"
        return 0
