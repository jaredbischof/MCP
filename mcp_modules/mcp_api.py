import glob, json, os, sys
from subsystem import subsystem

class mcp_api(subsystem):
    actions = [ 'start', 'stop', 'restart', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.state['status'] = { 'site' : 'online' }

    def start(self):
        files = glob.glob(self.apidir+"/*")
        if len(files) != 0:
            sys.stderr.write("ERROR: Cannot initialize mcp_api because API directory (" + self.apidir + ") is not empty\n")
            return 0

        for subsystem in self.json_conf['global']['subsystems']:
            subsystem = subsystem.strip();
            module = __import__(subsystem)
            myclass = getattr(module, subsystem)
            mysubsystem = myclass(self.MCP_dir)
            jstate = json.dumps(mysubsystem.state)
            f = open(self.apidir + "/" + subsystem, 'w')
            f.write(jstate)

        return 1

    def stop(self):
        for file_object in os.listdir(self.apidir):
            file_object_path = os.path.join(self.apidir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

        return 1

    def restart(self):
        self.stop()
        self.start()
        return 1
