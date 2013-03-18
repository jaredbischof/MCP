import json
import shlex, subprocess

class subsystem (object):
    def __init__(self, MCP_dir):
        self.MCP_dir = MCP_dir
        self.state = {}
        json_conf_file = open(self.MCP_dir+'conf/conf.json')
        self.json_conf = json.load(json_conf_file)
        self.apidir = self.json_conf['mcp_api']['dir'] + "/" + str(self.json_conf['mcp_api']['version'])

    def get_state(self):
        return self.state

    def run_cmd(self, cmd_str):
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise IOError("%s\n%s"%(" ".join(cmd), stderr))

        return stdout, stderr
