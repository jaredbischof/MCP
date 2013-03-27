from subsystem import subsystem

class pipeline(subsystem):
    actions = [ 'set_log', 'delete_log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.state['log_constraints'] = self.json_conf['pipeline']['log_constraints']
