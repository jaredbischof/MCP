import argparse
import commands
import json
import getpass, re, socket
import shlex, shutil, subprocess
import sys, time

class subsystem (object):
    def __init__(self, MCP_path):
        self.MCP_path = MCP_path
        matchObj = re.match(r'(^.*\/)', self.MCP_path)
        self.MCP_dir = matchObj.group(0)

        self.subsystem = self.__class__.__name__
        json_conf_file = open(self.MCP_dir+'conf/conf.json')
        self.json_conf = json.load(json_conf_file)
        self.apidir = self.json_conf['mcp_api']['dir'] + "/" + str(self.json_conf['mcp_api']['version'])
        self.log_level_max = self.json_conf['global']['log_level_max']
        self.log_level_min = self.json_conf['global']['log_level_min']

        self.req_host = ""
        if 'req_host' in self.json_conf[self.subsystem]:
            self.req_host = self.json_conf[self.subsystem]['req_host']

        self.req_user = ""
        if 'req_user' in self.json_conf[self.subsystem]:
            self.req_user = self.json_conf[self.subsystem]['req_user']

        self.state = { 'log_level':self.json_conf['global']['default_log_level'],
                       'subsystem':self.subsystem,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url':self.json_conf['global']['apiurl'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.subsystem
                     }

    def run(self, params):
        parser = argparse.ArgumentParser(prog='MCP ' + self.subsystem)
        parser.add_argument('action', metavar='action',
                       help="An action for the subsystem '" + self.subsystem + "' to perform. Available actions include: '" + "', '".join(self.actions) + "'")
        parser.add_argument('params', metavar='params', nargs=argparse.REMAINDER,
                       help="Additional arguments should specify an action followed by action parameters if required.")
        args = parser.parse_args(params)
        action = args.action
        params = args.params

        user = getpass.getuser()
        host = socket.gethostname()
        req_login = self.req_user + "@" + self.req_host
        if self.req_host != "" and self.req_user != "" and (user + "@" + host) != req_login:
            print "Handing off command to run as: " + req_login
            sout = self.run_cmd("sudo -s ssh " + " ".join([req_login, self.MCP_path, self.subsystem, action]) + " " + " ".join(params))
            return 1

        myaction = getattr(self, action)
        if params:
            myaction(params)
        else:
            myaction()

    def log(self, level):
        try:
            level = int(level)
        except ValueError:
            sys.stderr.write("ERROR: '" + level + "' is not an integer value.\n")
            return 0

        if level < self.log_level_min or level > self.log_level_max:
            sys.stderr.write("ERROR: '" + str(level) + "' is not a valid logging level.\n")
            return 0

        self.state['log_level'] = level
        self.state['updated'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        jstate = json.dumps(self.state)
        fname = self.apidir + "/" + self.__class__.__name__
        f = open(fname + ".tmp", 'w')
        f.write(jstate)
        shutil.move(fname + ".tmp", fname)

        return 1

    def run_cmd(self, cmd_str):
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = proc.communicate()
        if proc.returncode != 0 or serr != "":
            raise IOError("%s\n%s"%(" ".join(cmd), serr))
            return 0

        return sout
