import glob, json, os, sys
from subsystem import subsystem

class web(subsystem):
    actions = [ 'start', 'stop', 'set_log', 'delete_log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
        self.sites = []
        for site in self.json_conf['web']['sites']:
            self.sites.append(site['name'])

        self.state['status'] = {}
        for site in self.json_conf['web']['sites']:
            self.state['status'][site['name']] = ''

    def update_status(self):
        for site in self.json_conf['web']['sites']:
            self.state['status'][site['name']] = self.get_url_status(site['url'])

    def start(self, params):
        action = 'start'
        action_params = [ 'web_site' ]
        action_param_settings = { 'web_site' : [ str, "Web site to start ('" + "', '".join(self.sites) + "')"] }
        desc = "description: this action configures and restarts nginx to make the selected web_site active"
        self.parse_action_params(action, action_params, action_param_settings, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        site = params[0]
        if(site not in self.sites):
            sys.stderr.write("ERROR: '" + site + "' is not a valid site ('" + "', '".join(self.sites) + "')")
            return 1

        self.log_msg("ACTION : attempting to put the site " + site + " online")
        nginx_config_file = self.json_conf['global']['nginx_dir'] + "/" + site + ".conf"
        nginx_up_config_file = self.json_conf['global']['nginx_dir'] + "/" + site + ".up"
        os.unlink(nginx_config_file)
        os.symlink(nginx_up_config_file, nginx_config_file)
        sout, serr = self.run_cmd("/sbin/service nginx reload")
        if sout != "": sys.stdout.write(sout + "\n")
        if serr != "": sys.stdout.write(serr + "\n")
        self.log_msg("SUCCESS : site: " + site + " has been put online")

    def stop(self, params):
        action = 'stop'
        action_params = [ 'web_site' ]
        action_param_settings = { 'web_site' : [ str, "Web site to stop ('" + "', '".join(self.sites) + "')"] }
        desc = "description: this action configures and restarts nginx to make the selected web_site inactive"
        self.parse_action_params(action, action_params, action_param_settings, desc, params)
        if self.check_userhost() == -1:
            self.pass_mcp_cmd(action, params)
            return 0

        site = params[0]
        if(site not in self.sites):
            sys.stderr.write("ERROR: '" + site + "' is not a valid site ('" + "', '".join(self.sites) + "')")
            return 1

        self.log_msg("ACTION : attempting to put the site " + site + " offline")
        nginx_config_file = self.json_conf['global']['nginx_dir'] + "/" + site + ".conf"
        nginx_down_config_file = self.json_conf['global']['nginx_dir'] + "/" + site + ".down"
        os.unlink(nginx_config_file)
        os.symlink(nginx_down_config_file, nginx_config_file)
        sout, serr = self.run_cmd("/sbin/service nginx reload")
        if sout != "": sys.stdout.write(sout + "\n")
        if serr != "": sys.stdout.write(serr + "\n")
        self.log_msg("SUCCESS : site: " + site + " has been taken offline")
