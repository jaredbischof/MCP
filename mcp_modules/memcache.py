from subsystem import subsystem

class memcache(subsystem):
    actions = [ 'clear', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.memhost = self.json_conf['memcache']['memhost']

    def clear(self, params):
        self.parse_method_params('clear', [], {}, params)
        print "Clearing memcache:"
        sout, serr = self.run_cmd(self.MCP_dir + "bin/clear_memcache.pl " + self.memhost)
        print "memcache cleared!"
