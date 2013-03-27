import glob, json, os, sys
from subsystem import subsystem

class mcp_api(subsystem):
    actions = [ 'start', 'stop', 'restart', 'set_log', 'delete_log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        # Don't need to check url_status here because if MCP API is available then this subsystem is online
        self.state['status'] = { 'site' : 'online' }

    def start(self, params):
        action = 'start'
        desc = "description: this action writes the default files for the MCP API"
        self.parse_action_params(action, [], {}, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0
 
        self.log_msg("ACTION : attempting to initialize mcp_api")
        files = glob.glob(self.apidir+"/*")
        if len(files) != 0:
            sys.stderr.write("ERROR : Cannot initialize mcp_api because API directory (" + self.apidir + ") is not empty\n")
            return 1

        for subsystem in self.json_conf['global']['subsystems']:
            subsystem = subsystem.strip();
            module = __import__(subsystem)
            myclass = getattr(module, subsystem)
            mysubsystem = myclass(self.MCP_dir)
            mysubsystem.update_status()
            jstate = json.dumps(mysubsystem.state, sort_keys=True)
            f = open(self.apidir + "/" + subsystem, 'w')
            f.write(jstate)

        self.log_msg("SUCCESS : mcp_api started")

    def stop(self, params):
        action = 'stop'
        desc = "description: this action deletes the files of the MCP API"
        self.parse_action_params(action, [], {}, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        self.log_msg("ACTION : attempting to stop mcp_api")
        for file_object in os.listdir(self.apidir):
            file_object_path = os.path.join(self.apidir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

        self.log_msg("SUCCESS : mcp_api stopped")

    def restart(self, params):
        action = 'restart'
        desc = "description: this action deletes then writes the default files for the MCP API"
        self.parse_action_params(action, [], {}, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        self.stop(params)
        self.start(params)
