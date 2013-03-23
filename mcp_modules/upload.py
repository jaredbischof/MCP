import os, json, sys
from subsystem import subsystem

class upload(subsystem):
    actions = [ 'lock_page', 'unlock_page', 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.state['status'] = {}

        self.lock_file = self.json_conf['upload']['lock_dir'] + "/upload.lock"
        if os.path.isfile(self.lock_file):
            self.state['status']['page'] = "offline"
        else:
            self.state['status']['page'] = "online"

    def lock_page(self, params):
        action = 'lock_page'
        desc = "description: this action creates the lock file for the MG-RAST production upload page and thus disables that page."
        self.parse_action_params(action, [], {}, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        fh = file(self.lock_file, 'a')
        try:
            os.utime(self.lock_file, None)
        finally:
            fh.close()

        self.state['status']['page'] = "offline"
        jstate = json.dumps(self.state)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)

    def unlock_page(self, params):
        action = 'unlock_page'
        desc = "description: this action deletes the lock file for the MG-RAST production upload page and thus enables that page."
        self.parse_action_params(action, [], {}, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        if os.path.isfile(self.lock_file):
            os.unlink(self.lock_file)

        self.state['status']['page'] = "online"
        jstate = json.dumps(self.state)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
