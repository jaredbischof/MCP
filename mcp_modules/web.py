import glob, json, os, sys
from subsystem import subsystem

class web(subsystem):
    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

    def update_status(self, params):
        function = 'update_status'
        desc = "description: this function updates the status of the web subsystem in the control api"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to update the web subsystem api status'" ])
        self.run_action("update_web_status", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : web subsystem api status updated'" ])

    def start_prod(self, params):
        function = 'start_prod'
        desc = "description: this function configures and restarts nginx to turn on the MG-RAST production website"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".up"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn on the MG_RAST production website'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST production website started'" ])

    def stop_prod(self, params):
        function = 'stop_prod'
        desc = "description: this function configures and restarts nginx to turn off the MG-RAST production website"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".down"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn off the MG_RAST production website'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST production website stopped'" ])

    def start_dev(self, params):
        function = 'start_dev'
        desc = "description: this function configures and restarts nginx to turn on the MG-RAST dev website"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".up"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn on the MG_RAST dev website'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST dev website started'" ])

    def stop_dev(self, params):
        function = 'stop_dev'
        desc = "description: this function configures and restarts nginx to turn off the MG-RAST dev website"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".down"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn off the MG_RAST dev website'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST dev website stopped'" ])

    def start_api(self, params):
        function = 'start_api'
        desc = "description: this function configures and restarts nginx to turn on the MG-RAST API"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".up"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn on the MG_RAST API'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST API started'" ])

    def stop_api(self, params):
        function = 'stop_api'
        desc = "description: this function configures and restarts nginx to turn off the MG-RAST API"
        self.parse_function_params(function, [], {}, desc, params)

        site_name = self.json_conf['web']['functions'][function]['name']
        nginx_dir = self.json_conf['web']['functions'][function]['nginx_dir']
        nginx_config_link = nginx_dir + "/" + site_name + ".conf"
        nginx_config_file = nginx_dir + "/" + site_name + ".down"

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to turn off the MG_RAST API'" ])
        self.run_action("edit_nginx_config", self.get_req_login(function), [ nginx_config_link, nginx_config_file ])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : MG_RAST API stopped'" ])
