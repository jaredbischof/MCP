from subsystem import subsystem

class queue(subsystem):
    actions = [ 'start', 'stop', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

        # getting status of queues
        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q batch")
        lines = sout.splitlines()
        batch_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q fast")
        lines = sout.splitlines()
        fast_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        self.state['status'] = { 'batch': batch_status, 'fast': fast_status }

    def start(self, params):
        action = 'start'
        self.parse_action_params(action, [], {}, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        print "Starting nagasaki pipeline:"
        sout, serr = self.run_cmd("/usr/local/bin/qstart batch")
        print "nagasaki pipeline started!"

    def stop(self, params):
        action = 'stop'
        self.parse_action_params(action, [], {}, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        print "Stopping nagasaki pipeline:"
        sout, serr = self.run_cmd("/usr/local/bin/qstop batch")
        print "nagasaki pipeline stopped!"
