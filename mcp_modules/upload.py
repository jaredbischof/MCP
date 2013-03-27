import os, json, sys
from subsystem import subsystem

class upload(subsystem):
    actions = [ 'lock_page', 'unlock_page', 'set_log', 'delete_log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.lock_file = self.json_conf['upload']['lock_dir'] + "/upload.lock"
        self.state['status'] = {}
        self.state['status']['page'] = ''

    def update_status(self):
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

        self.log_msg("ACTION : attempting to disable upload page")

        fh = file(self.lock_file, 'a')
        try:
            os.utime(self.lock_file, None)
        finally:
            fh.close()

        self.state['status']['page'] = "offline"
        jstate = json.dumps(self.state, sort_keys=True)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        self.log_msg("SUCCESS : upload page disabled")

    def unlock_page(self, params):
        action = 'unlock_page'
        desc = "description: this action deletes the lock file for the MG-RAST production upload page and thus enables that page."
        self.parse_action_params(action, [], {}, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        self.log_msg("ACTION : attempting to enable upload page")

        if os.path.isfile(self.lock_file):
            os.unlink(self.lock_file)

        self.state['status']['page'] = "online"
        jstate = json.dumps(self.state, sort_keys=True)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        self.log_msg("SUCCESS : upload page enabled")
