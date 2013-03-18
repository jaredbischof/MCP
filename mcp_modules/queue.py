import time
from subsystem import subsystem

class queue(subsystem):
    actions = "start, stop"

    def __init__(self, MCP_dir):
        subsystem.__init__(self, MCP_dir)

        # getting status of queues
        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q batch")
        lines = sout.splitlines()
        batch_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q fast")
        lines = sout.splitlines()
        fast_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        self.state = { 'resource':self.__class__.__name__,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S"),
                       'url':self.json_conf['global']['apiurl'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.__class__.__name__,
                       'status': { 'batch': batch_status,
                                   'fast': fast_status
                                 }
                     }

    def start(self):
        print "Starting nagasaki pipeline:"
        sout, serr = self.run_cmd("/usr/local/bin/qstart batch")
        print "nagasaki pipeline started!"
        return 0

    def stop(self):
        print "Stopping nagasaki pipeline:"
        sout, serr = self.run_cmd("/usr/local/bin/qstop batch")
        print "nagasaki pipeline stopped!"
        return 0
