import argparse
import commands
import json
import getpass, re, socket
import shlex, shutil, subprocess
import sys, time, os
import textwrap
import urllib
import syslog

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

        self.state = { 'log_levels': [ { 'level' : self.json_conf['global']['default_log_level'], 'constraints' : {} } ],
                       'subsystem' : self.subsystem,
                       'updated' : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url' : self.json_conf['global']['api_url'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.subsystem
                     }

    def update_status(self):
        return 0

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
            parser.add_argument(p, type=action_param_settings[p][0], help=action_param_settings[p][1])
        args = vars(parser.parse_args(params))
        for i in args.keys():
            if(args[i] == None):
                del args[i]
        return args

    def set_log(self, params):
        action = 'set_log'
        action_params = [ 'level' ]
        action_param_settings = { 'level' : [ int, "Log level to set for " + self.subsystem + " (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")" ] }
        desc = "description: this action adds or sets the log level for the '" + self.subsystem + "' subsystem with any added options as contraints for this log setting"

        log_constraints = {}
        if 'log_constraints' in self.json_conf[self.subsystem]:
            log_constraints = self.json_conf[self.subsystem]['log_constraints']

        for c in log_constraints:
            name = c['name']
            type = c['type']
            choices = []
            if 'choices' in c:
                choices = c['choices']
            action_params.append("--" + name)
            if type == "string":
                action_param_settings["--" + name] = [ str, ", ".join(choices) ]
            elif type == "integer":
                action_param_settings["--" + name] = [ int, "integer value" ]
            else:
                sys.stderr.write("ERROR: Unknown log constraint type '" + type + "'. Must be of type 'string' or 'integer'")
                return 1

        aparams = self.parse_action_params(action, action_params, action_param_settings, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        level = aparams['level']
        del aparams['level']
        if level < self.log_level_min or level > self.log_level_max:
            sys.stderr.write("ERROR: '" + str(level) + "' is not a valid logging level (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")\n")
            return 1

        if(len(params) == 1):
            self.log_msg("ACTION : attempting to set log level to " + str(level) + " for subsystem '" + self.subsystem + "'")
        else:
            self.log_msg("ACTION : attempting to set log level to " + str(level) + " for subsystem '" + self.subsystem + "' with constraints " + str(aparams))

        self.update_state_from_api()
        self.update_status()

        api_constraints = {}
        for key, value in aparams.iteritems():
            api_constraints[key] = str(value)

        constraints_found = 0
        for log_level_set in self.state['log_levels']:
            if log_level_set['constraints'] == api_constraints:
                log_level_set['level'] = level
                constraints_found = 1

        if constraints_found == 0:
            self.state['log_levels'].append( { 'level' : level, 'constraints' : api_constraints } )

        self.state['updated'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        jstate = json.dumps(self.state, sort_keys=True)
        fname = self.apidir + "/" + self.__class__.__name__
        f = open(fname + ".tmp", 'w')
        f.write(jstate)
        shutil.move(fname + ".tmp", fname)
        if(len(params) == 1):
            self.log_msg("SUCCESS : log level set to " + str(level) + " for subsystem '" + self.subsystem + "'")
        else:
            self.log_msg("SUCCESS : log level set to " + str(level) + " for subsystem '" + self.subsystem + "' with constraints " + str(aparams))

    def delete_log(self, params):
        action = 'delete_log'
        action_params = []
        action_param_settings = {}
        desc = "description: this action adds or sets the log level for the '" + self.subsystem + "' subsystem with any added options as contraints for this log setting"

        log_constraints = {}
        if 'log_constraints' in self.json_conf[self.subsystem]:
            log_constraints = self.json_conf[self.subsystem]['log_constraints']

        for c in log_constraints:
            name = c['name']
            type = c['type']
            choices = []
            if 'choices' in c:
                choices = c['choices']
            action_params.append("--" + name)
            if type == "string":
                action_param_settings["--" + name] = [ str, ", ".join(choices) ]
            elif type == "integer":
                action_param_settings["--" + name] = [ int, "integer value" ]
            else:
                sys.stderr.write("ERROR: Unknown log constraint type '" + type + "'. Must be of type 'string' or 'integer'\n")
                return 1

        aparams = self.parse_action_params(action, action_params, action_param_settings, desc, params)

        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        if(len(params) > 0):
            self.log_msg("ACTION : attempting to delete log level from subsystem '" + self.subsystem + "' with constraints " + str(aparams))
        else:
            sys.stderr.write("ERROR: Cannot delete default log level for subsystem '" + self.subsystem + "'. You must provide some constraints.\n")
            return 1

        self.update_state_from_api()
        self.update_status()

        api_constraints = {}
        for key, value in aparams.iteritems():
            api_constraints[key] = str(value)

        constraints_found = 0
        for i, log_level_set in enumerate(self.state['log_levels']):
            if log_level_set['constraints'] == api_constraints:
                del self.state['log_levels'][i]
                constraints_found = 1

        if constraints_found == 0:
            sys.stderr.write("ERROR: Could not find a log level for subsystem '" + self.subsystem + "' with constraints " + str(aparams) + ". Nothing was deleted.\n")
            return 1

        self.state['updated'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        jstate = json.dumps(self.state, sort_keys=True)
        fname = self.apidir + "/" + self.__class__.__name__
        f = open(fname + ".tmp", 'w')
        f.write(jstate)
        shutil.move(fname + ".tmp", fname)
        self.log_msg("SUCCESS : log level deleted from subsystem '" + self.subsystem + "' with constraints " + str(aparams))

    def log_msg(self, msg): 
        syslog.syslog(syslog.LOG_INFO, msg)
        print msg

    def update_state_from_api(self):
        file_path = self.apidir + "/" + self.subsystem
        if os.path.isfile(file_path):
            try:
                json_state_file = open(self.apidir + "/" + self.subsystem)
            except IOError:
                sys.stderr.write("ERROR: could not open the file '" + file_path + "'")

        self.state = json.load(json_state_file)
        return True

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
