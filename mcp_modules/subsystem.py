import argparse
import json
import getpass, re, socket
import shlex, subprocess
import sys
import urllib

class subsystem (object):
    def __init__(self, MCP_path):
        self.MCP_path = MCP_path
        matchObj = re.match(r'(^.*\/)', self.MCP_path)
        self.MCP_dir = matchObj.group(0)
        json_conf_file = open(self.MCP_dir+'conf/conf.json')
        self.json_conf = json.load(json_conf_file)

        self.subsystem = self.__class__.__name__
        self.log_level_min = self.json_conf['global']['log_level_min']
        self.log_level_max = self.json_conf['global']['log_level_max']

    def get_req_login(self, function):
        if self.json_conf[self.subsystem]["functions"][function]["req_user"] and self.json_conf[self.subsystem]["functions"][function]["req_host"]:
            return self.json_conf[self.subsystem]["functions"][function]["req_user"] + '@' + self.json_conf[self.subsystem]["functions"][function]["req_host"]
        else:
            return 'ANY'

    def update_status(self, params):
        function = 'update_status'
        desc = "description: this function updates the status of the " + self.subsystem + " subsystem in the control API"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to set " + self.subsystem + " updated variable to current timestamp'" ])
        self.run_action("update_subsystem_timestamp", self.get_req_login(function), [ self.subsystem ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : " + self.subsystem + " updated variable set to current timestamp'" ])
        return 0

    def parse_subsystem_params(self, params):
        parser = argparse.ArgumentParser(prog='MCP ' + self.subsystem)
        parser.add_argument('function', metavar='function',
                       help="A function for the subsystem '" + self.subsystem + "' to perform. Available functions include: '" + "', '".join(self.json_conf[self.subsystem]['functions'].keys()) + "'")
        parser.add_argument('params', metavar='params', nargs=argparse.REMAINDER,
                       help="The function may accept additional parameters.")
        args = parser.parse_args(params)
        function = args.function
        function_params = args.params
        return function, function_params

    def parse_function_params(self, function, function_params, function_param_settings, desc, params):
        parser = argparse.ArgumentParser(prog='MCP ' + self.subsystem + " " + function, description=desc)
        for p in function_params:
            parser.add_argument(p, type=function_param_settings[p][0], help=function_param_settings[p][1])
        args = vars(parser.parse_args(params))
        for i in args.keys():
            if(args[i] == None):
                del args[i]
        return args

    def set_log(self, params):
        function = 'set_log'
        function_params = [ 'level' ]
        function_param_settings = { 'level' : [ int, "Log level to set for " + self.subsystem + " (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")" ] }
        desc = "description: this function adds or sets the log level for the '" + self.subsystem + "' subsystem with any added options as contraints for this log setting"

        if 'log_constraints' in self.json_conf[self.subsystem]:
            for c in self.json_conf[self.subsystem]['log_constraints']:
                name = c['name']
                type = c['type']
                choices = []

                if 'choices' in c:
                    choices = c['choices']
                function_params.append("--" + name)

                if type == "string":
                    function_param_settings["--" + name] = [ str, ", ".join(choices) ]
                elif type == "integer":
                    function_param_settings["--" + name] = [ int, "integer value" ]
                else:
                    sys.stderr.write("ERROR: Unknown log constraint type '" + type + "'. Must be of type 'string' or 'integer'")
                    return 1

        fparams = self.parse_function_params(function, function_params, function_param_settings, desc, params)

        level = fparams['level']
        del fparams['level']
        if level < self.log_level_min or level > self.log_level_max:
            sys.stderr.write("ERROR: '" + str(level) + "' is not a valid logging level (" + str(self.log_level_min) + "-" + str(self.log_level_max) + ")\n")
            return 1

        log_msg1 = ""
        log_msg2 = ""
        if(len(params) == 1):
            log_msg1 = "REQUEST : attempting to set log level to " + str(level) + " for subsystem '" + self.subsystem + "'"
            log_msg2 = "SUCCESS : log level set to " + str(level) + " for subsystem '" + self.subsystem + "'"
        else:
            log_msg1 = "REQUEST : attempting to set log level to " + str(level) + " for subsystem '" + self.subsystem + "' with constraints " + str(fparams)
            log_msg2 = "SUCCESS : log level set to " + str(level) + " for subsystem '" + self.subsystem + "' with constraints " + str(fparams)

        req_userhost = self.json_conf[self.subsystem]["functions"][function]["req_user"] + '@' + self.json_conf[self.subsystem]["functions"][function]["req_host"]

        options_str = ""
        for option in fparams.keys():
            options_str += "--" + option + "=" + str(fparams[option]) + " "

        self.run_action("log_msg", "ANY", [ "INFO", "'" + log_msg1 + "'" ])
        self.run_action("set_log_level", req_userhost, [ self.subsystem, str(level), options_str ])
        self.run_action("log_msg", "ANY", [ "INFO", "'" + log_msg2 + "'" ])

        # Running the update_status() function here (this only does anything if defined for this subsystem,
        #    otherwise this just runs the update_status() function from parent class: subsystem.py which
        #    simply sets the 'updated' api variable to the current time.)
        self.update_status("")

    def delete_log(self, params):
        function = 'delete_log'
        function_params = []
        function_param_settings = {}
        desc = "description: this function deletes the log level for the '" + self.subsystem + "' subsystem with options as contraints for this log setting, the default log level cannot be deleted."

        if 'log_constraints' in self.json_conf[self.subsystem]:
            for c in self.json_conf[self.subsystem]['log_constraints']:
                name = c['name']
                type = c['type']
                choices = []

                if 'choices' in c:
                    choices = c['choices']
                function_params.append("--" + name)

                if type == "string":
                    function_param_settings["--" + name] = [ str, ", ".join(choices) ]
                elif type == "integer":
                    function_param_settings["--" + name] = [ int, "integer value" ]
                else:
                    sys.stderr.write("ERROR: Unknown log constraint type '" + type + "'. Must be of type 'string' or 'integer'\n")
                    return 1

        fparams = self.parse_function_params(function, function_params, function_param_settings, desc, params)

        if(len(fparams) < 1):
            sys.stderr.write("ERROR: Cannot delete default log level for subsystem '" + self.subsystem + "'. You must provide some constraints.\n")
            return 1

        req_userhost = self.json_conf[self.subsystem]["functions"][function]["req_user"] + '@' + self.json_conf[self.subsystem]["functions"][function]["req_host"]

        options_str = ""
        for option in fparams.keys():
            options_str += "--" + option + "=" + str(fparams[option]) + " "

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to delete log level from subsystem " + self.subsystem + " with constraints " + str(fparams) + "'" ])
        self.run_action("delete_log_level", req_userhost, [ self.subsystem, options_str ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : log level deleted from subsystem " + self.subsystem + " with constraints " + str(fparams) + "'" ])

        # Running the update_status() function here (this only does anything if defined for this subsystem,
        #    otherwise this just runs the update_status() function from parent class: subsystem.py which
        #    simply sets the 'updated' api variable to the current time.)
        self.update_status("")

    def run_action(self, action, req_userhost, args):
        arg_str = " ".join(args)

        cmd_str = self.MCP_dir + "bin/" + action + " " + arg_str
        print "Running " + cmd_str

        if req_userhost == "ANY":
            sout, serr = self.run_cmd(cmd_str)
        else:
            print "Attempting to run " + action + " as " + req_userhost
            sout, serr = self.run_cmd("sudo -s ssh " + " " + req_userhost + " " + cmd_str)

        if sout != "": sys.stdout.write(sout + "\n")
        if serr != "": sys.stdout.write(serr + "\n")

    def run_cmd(self, cmd_str):
        cmd = shlex.split(str(cmd_str))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = proc.communicate()
        if proc.returncode != 0 and serr != "":
            print serr
            exit(1)
        return sout, serr
