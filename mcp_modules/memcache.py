import json, time
from mcp_base import mcp_base

class memcache(mcp_base):
    actions = "clear"

    def __init__(self, MCP_dir):
        mcp_base.__init__(self, MCP_dir)
        self.state = { 'resource':self.__class__.__name__,
                       'date':time.strftime("%Y-%m-%d %H:%M:%S")
                     }

    def clear(self):
        print "Clearing memcache:"
        sout, serr = self.run_cmd(self.MCP_dir + "bin/clear_memcache.pl " + self.memhost)
        print "memcache cleared!"
        return 0
