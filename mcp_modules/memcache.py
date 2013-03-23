from subsystem import subsystem

class memcache(subsystem):
    actions = [ 'clear', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.prog = self.json_conf['memcache']['prog']
        self.memhost = self.json_conf['memcache']['memhost']

    def clear(self, params):
        action = 'clear'
        desc = "description: this action clears the memcache"
        self.parse_action_params(action, [], {}, desc, params)
        cmd = self.MCP_dir + self.prog + " " + self.memhost

        if self.check_userhost() == -1:
            print "ACTION: attempting to clear memcache as: " + self.req_login
            sout, serr = self.run_cmd("sudo -s ssh " + self.req_login + " " + cmd)
            print "SUCCESS: memcache cleared!"
            return 0

        print "ACTION: clearing memcache"
        sout, serr = self.run_cmd(cmd)
        print "SUCCESS: memcache cleared"
