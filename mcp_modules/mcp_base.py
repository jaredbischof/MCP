class mcp_base (object):
    def __init__(self, MCP_dir):
        from ConfigParser import SafeConfigParser
        self.MCP_dir = MCP_dir
        self.state = {}
        parser = SafeConfigParser()
        parser.read(self.MCP_dir+'conf/conf.ini')
        self.apidir = parser.get('api', 'dir') + "/" + parser.get('api', 'version')
        self.memhost = parser.get('hosts', 'memhost')
        self.services = parser.get('global', 'services')

    def get_state(self):
        return self.state

    def run_cmd(self, cmd_str):
        import shlex, subprocess
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise IOError("%s\n%s"%(" ".join(cmd), stderr))

        return stdout, stderr
