from subsystem import subsystem

class memcache(subsystem):
    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

    def clear(self, params):
        function = 'clear'
        desc = "description: this function clears the memcache"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to clear " + self.subsystem + "'" ])
        self.run_action("clear_memcache", self.get_req_login(function), [ "'" + self.json_conf[self.subsystem]["memhost"] + "'" ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : " + self.subsystem + " cleared'" ])
