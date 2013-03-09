import json, time
from mcp_base import mcp_base

class nagasaki(mcp_base):
    actions = "start, stop"

    def __init__(self, MCP_dir):
        mcp_base.__init__(self, MCP_dir)

        # getting status of queues
        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q batch")
        lines = sout.splitlines()
        batch_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        sout, serr = self.run_cmd("/usr/local/bin/qstat -Q fast")
        lines = sout.splitlines()
        fast_status = 'online' if lines[len(lines)-1].split()[3] == 'yes' else 'offline'

        self.state = { 'resource':self.__class__.__name__,
                       'date':time.strftime("%Y-%m-%d %H:%M:%S"),
                       'queues': [ { 'name': 'batch',
                                     'status': batch_status
                                   },
                                   { 'name': 'fast',
                                     'status': fast_status
                                   } ]
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
