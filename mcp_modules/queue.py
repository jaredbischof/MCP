from subsystem import subsystem

class queue(subsystem):
    actions = [ 'start', 'stop', 'set_log', 'delete_log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.state['log_constraints'] = self.json_conf['queue']['log_constraints']
        self.state['status'] = {}
        for queue in self.json_conf['queue']['queues']:
            self.state['status'][queue] = ''

    def update_status(self):
        # getting status of queues
        for queue in self.json_conf['queue']['queues']:
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
        self.log_msg("ACTION : attempting to start " + queue + " queue")
        sout, serr = self.run_cmd("/usr/local/bin/qstart " + queue)
        self.log_msg("SUCCESS : " + queue + " queue started")

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
        self.log_msg("ACTION : attempting to stop " + queue + " queue")
        sout, serr = self.run_cmd("/usr/local/bin/qstop " + queue)
        self.log_msg("SUCCESS : " + queue + " queue stopped")
