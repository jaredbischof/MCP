import glob, json, os, sys
from subsystem import subsystem

class mcp_api(subsystem):
    actions = [ 'start', 'stop', 'restart', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.state['status'] = { 'site' : 'online' }

    def start(self, params):
        self.parse_method_params('start', [], {}, params)
        files = glob.glob(self.apidir+"/*")
        if len(files) != 0:
            sys.stderr.write("ERROR: Cannot initialize mcp_api because API directory (" + self.apidir + ") is not empty\n")
            return 1

        for subsystem in self.json_conf['global']['subsystems']:
            subsystem = subsystem.strip();
            module = __import__(subsystem)
            myclass = getattr(module, subsystem)
            mysubsystem = myclass(self.MCP_dir)
            jstate = json.dumps(mysubsystem.state)
            f = open(self.apidir + "/" + subsystem, 'w')
            f.write(jstate)

    def stop(self, params):
        self.parse_method_params('stop', [], {}, params)
        for file_object in os.listdir(self.apidir):
            file_object_path = os.path.join(self.apidir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    def restart(self, params):
        self.parse_method_params('restart', [], {}, params)
        self.stop(params)
        self.start(params)
