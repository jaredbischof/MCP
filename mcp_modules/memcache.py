from mcp_base import mcp_base

class memcache(mcp_base):
    actions = "clear"

    def clear(self):
        """Clears the perl memcache server"""
        print "Clearing memcache:"
        sout, serr = self.run_cmd(self.MCP_dir + "bin/clear_memcache.pl " + self.memhost)
        print "memcache cleared!"
        return
