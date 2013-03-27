from subsystem import subsystem

class memcache(subsystem):
    actions = [ 'clear', 'set_log', 'delete_log' ]

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
            self.log_msg("ACTION : Attempting to clear memcache as " + self.req_login)
            sout, serr = self.run_cmd("sudo -s ssh " + self.req_login + " " + cmd)
            self.log_msg("SUCCESS : memcache cleared")
            return 0

        self.log_msg("ACTION : Attempting to clear memcache")
        sout, serr = self.run_cmd(cmd)
        self.log_msg("SUCCESS : memcache cleared")
