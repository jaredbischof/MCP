import argparse
import commands
import json
import getpass, re, socket
import shlex, shutil, subprocess
import sys, time
import textwrap
import urllib

class subsystem (object):
    def __init__(self, MCP_path):
        self.MCP_path = MCP_path
        matchObj = re.match(r'(^.*\/)', self.MCP_path)
        self.MCP_dir = matchObj.group(0)

        self.subsystem = self.__class__.__name__
        json_conf_file = open(self.MCP_dir+'conf/conf.json')
        self.json_conf = json.load(json_conf_file)
        self.apidir = self.json_conf['mcp_api']['dir'] + "/" + str(self.json_conf['mcp_api']['version'])
        self.log_level_min = self.json_conf['global']['log_level_min']
        self.log_level_max = self.json_conf['global']['log_level_max']

        self.req_host = ""
        if 'req_host' in self.json_conf[self.subsystem]:
            self.req_host = self.json_conf[self.subsystem]['req_host']

        self.req_user = ""
        if 'req_user' in self.json_conf[self.subsystem]:
            self.req_user = self.json_conf[self.subsystem]['req_user']

        self.req_login = ""
        if self.req_host != "" and self.req_user != "":
            self.req_login = self.req_user + "@" + self.req_host

        self.state = { 'log_level':self.json_conf['global']['default_log_level'],
                       'subsystem':self.subsystem,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url':self.json_conf['global']['api_url'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.subsystem
                     }

    def parse_subsystem_params(self, params):
        parser = argparse.ArgumentParser(prog='MCP ' + self.subsystem)
        parser.add_argument('action', metavar='action',
                       help="An action for the subsystem '" + self.subsystem + "' to perform. Available actions include: '" + "', '".join(self.actions) + "'")
        parser.add_argument('params', metavar='params', nargs=argparse.REMAINDER,
                       help="The action may be followed by action parameters.")
        args = parser.parse_args(params)
        action = args.action
        action_params = args.params
        return action, action_params

    def check_userhost(self):
        user = getpass.getuser()
        host = socket.gethostname()
        if self.req_login != "" and (user + "@" + host) != self.req_login:
            return -1

        return 0

    def pass_mcp_cmd(self, action, params):
        print "Attempting to run command as: " + self.req_login
        sout, serr = self.run_cmd("sudo -s ssh " + " ".join([self.req_login, self.MCP_path, self.subsystem, action]) + " " + " ".join(params))
        if sout != "": sys.stdout.write(sout + "\n")
        if serr != "": sys.stdout.write(serr + "\n")

    def parse_action_params(self, action, action_params, action_param_settings, desc, params):
        parser = argparse.ArgumentParser(prog='MCP ' + self.subsystem + " " + action, description=desc)
        for p in action_params:
            parser.add_argument(p, type=action_param_settings[p][0], metavar=p, help=action_param_settings[p][1])
        args = parser.parse_args(params)

    def log(self, params):
        action = 'log'
        action_params = [ 'level' ]
        action_param_settings = { 'level' : [ int, "Log level to set for " + self.subsystem + " (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")" ] }
        desc = "description: this action sets the log level for the '" + self.subsystem + "' subsystem"
        self.parse_action_params(action, action_params, action_param_settings, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        level = params[0]
        try:
            level = int(level)
        except ValueError:
            sys.stderr.write("ERROR: '" + level + "' is not an integer value.\n")
            return 1

        if level < self.log_level_min or level > self.log_level_max:
            sys.stderr.write("ERROR: '" + str(level) + "' is not a valid logging level (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")\n")
            return 1

        self.state['log_level'] = level
        self.state['updated'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        jstate = json.dumps(self.state)
        fname = self.apidir + "/" + self.__class__.__name__
        f = open(fname + ".tmp", 'w')
        f.write(jstate)
        shutil.move(fname + ".tmp", fname)

    def get_url_status(self, url):
        code = urllib.urlopen(url).getcode()
        if code == 200:
            return 'online'
        else:
            return 'offline'

    def run_cmd(self, cmd_str):
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = proc.communicate()
        if proc.returncode != 0 and serr != "":
            print serr
            exit(1)
        return sout, serr
