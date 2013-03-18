import json, sys, time
from subsystem import subsystem

class mlog(subsystem):
    actions = "set"

    def __init__(self, MCP_dir):
        subsystem.__init__(self, MCP_dir)
        self.state = { 'resource':self.__class__.__name__,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url':self.json_conf['global']['apiurl'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.__class__.__name__,
                       'log_levels':{}
                     }

        for component in self.json_conf['mlog']['log_levels']:
            self.state['log_levels'][component] = self.json_conf['mlog']['log_levels'][component]

    def set(self, component, level):
        if component not in self.json_conf['mlog']['log_levels']:
            sys.stderr.write("ERROR: '" + component + "' is not a valid logging component.\n")
            return 0
        else:
            try:
                int(level)
            except ValueError:
                sys.stderr.write("ERROR: '" + level + "' is not an integer value.\n")
                return 0
            self.state['log_levels'][component] = int(level)
            self.state['updated'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            jstate = json.dumps(self.get_state())
            f = open(self.apidir + "/" + self.__class__.__name__, 'w')
            f.write(jstate)
        return 1
