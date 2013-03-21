from subsystem import subsystem

class queue(subsystem):
    actions = [ 'start', 'stop', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

        # getting status of queues
        sout = self.run_cmd("/usr/local/bin/qstat -Q batch")
        lines = sout.splitlines()
        batch_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        sout = self.run_cmd("/usr/local/bin/qstat -Q fast")
        lines = sout.splitlines()
        fast_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        self.state['status'] = { 'batch': batch_status, 'fast': fast_status }

    def start(self):
        print "Starting nagasaki pipeline:"
        sout = self.run_cmd("/usr/local/bin/qstart batch")
        print "nagasaki pipeline started!"
        return 1

    def stop(self):
        print "Stopping nagasaki pipeline:"
        sout = self.run_cmd("/usr/local/bin/qstop batch")
        print "nagasaki pipeline stopped!"
        return 1
