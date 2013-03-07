from mcp_base import mcp_base

class nagasaki(mcp_base):
    actions = "start, stop"
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
