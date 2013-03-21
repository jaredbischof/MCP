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

    def lock_page(self):
        fh = file(self.lock_file, 'a')
        try:
            os.utime(self.lock_file, None)
        finally:
            fh.close()

        self.state['status']['page'] = "offline"
        jstate = json.dumps(self.state)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        return 1

    def unlock_page(self):
        if os.path.isfile(self.lock_file):
            os.unlink(self.lock_file)

        self.state['status']['page'] = "online"
        jstate = json.dumps(self.state)
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        return 1
