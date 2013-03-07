class mcp_base (object):
    def __init__(self, MCP_dir):
        from ConfigParser import SafeConfigParser
        self.MCP_dir = MCP_dir
        parser = SafeConfigParser()
        parser.read(self.MCP_dir+'conf/conf.ini')
        self.apidir = parser.get('dirs', 'apidir')
        self.memhost = parser.get('hosts', 'memhost')
        self.services = parser.get('global', 'services')

    def run_cmd(self, cmd_str):
        import shlex, subprocess
        print cmd_str
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise IOError("%s\n%s"%(" ".join(cmd), stderr))

        return stdout, stderr
