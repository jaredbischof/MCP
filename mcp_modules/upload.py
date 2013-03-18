import os, json, sys, time
from subsystem import subsystem

class upload(subsystem):
    actions = "lock_page, unlock_page"

    def __init__(self, MCP_dir):
        subsystem.__init__(self, MCP_dir)
        self.state = { 'resource':self.__class__.__name__,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url':self.json_conf['global']['apiurl'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.__class__.__name__,
                       'status':{}
                     }

        self.lock_file = self.json_conf['upload']['lock_dir'] + "/upload.lock"
        if os.path.isfile(self.lock_file):
            self.state['status']['page'] = "locked"
        else:
            self.state['status']['page'] = "not locked"

    def lock_page(self):
        fh = file(self.lock_file, 'a')
        try:
            os.utime(self.lock_file, None)
        finally:
            fh.close()

        self.state['status']['page'] = "locked"
        jstate = json.dumps(self.get_state())
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        return 1

    def unlock_page(self):
        if os.path.isfile(self.lock_file):
            os.unlink(self.lock_file)

        self.state['status']['page'] = "not locked"
        jstate = json.dumps(self.get_state())
        f = open(self.apidir + "/" + self.__class__.__name__, 'w')
        f.write(jstate)
        return 1
