from subsystem import subsystem

class queue(subsystem):
    actions = [ 'start', 'stop', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.queues = [ 'batch', 'fast' ]
        self.state['status'] = {}

        # getting status of queues
        for queue in self.queues:
            sout, serr = self.run_cmd("/usr/local/bin/qstat -Q " + queue)
            lines = sout.splitlines()
            status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'
            self.state['status'][queue] = status

    def start(self, params):
        action = 'start'
        action_params = [ 'queue_name' ]
        action_param_settings = { 'queue_name' : [ str, "name of the queue to run qstart on ('" + "', '".join(self.state['status']) + "')"] }
        desc = "description: this action runs qstart on the selected queue ('" + "', '".join(self.state['status']) + "')"
        self.parse_action_params(action, action_params, action_param_settings, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        queue = params[0]
        print "ACTION: Starting " + queue + " queue"
        sout, serr = self.run_cmd("/usr/local/bin/qstart " + queue)
        print "SUCCESS: " + queue + " queue started!"

    def stop(self, params):
        action = 'stop'
        action_params = [ 'queue_name' ]
        action_param_settings = { 'queue_name' : [ str, "name of the queue to run qstop on ('" + "', '".join(self.state['status']) + "')"] }
        desc = "description: this action runs qstop on the selected queue ('" + "', '".join(self.state['status']) + "')"
        self.parse_action_params(action, action_params, action_param_settings, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        queue = params[0]
        print "ACTION: Stopping " + queue + " queue"
        sout, serr = self.run_cmd("/usr/local/bin/qstop " + queue)
        print "SUCCESS: " + queue + " queue stopped!"
