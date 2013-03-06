class memcache(object):
    actions = "clear"
    def clear():
        """Clears the perl memcache server"""
        print "Clearing memcache:"
        sout, serr = run_cmd(MCP_dir + "bin/clear_memcache.pl " + parser.get('hosts', 'memhost'))
        print "memcache cleared!"
