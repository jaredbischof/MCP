import shlex, subprocess
from ConfigParser import SafeConfigParser

class subsystem (object):
    def __init__(self, MCP_dir):
        self.MCP_dir = MCP_dir
        self.state = {}
        self.parser = SafeConfigParser()
        self.parser.read(self.MCP_dir+'conf/conf.ini')

    def get_state(self):
        return self.state

    def run_cmd(self, cmd_str):
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise IOError("%s\n%s"%(" ".join(cmd), stderr))

        return stdout, stderr
