from subsystem import subsystem

class control_api(subsystem):
    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

    def start(self, params):
        function = 'start'
        desc = "description: this function writes the default files for the control API"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to start " + self.subsystem + "'" ])
        self.run_action("start_control_api", self.get_req_login(function), [])

        for subsystem in self.json_conf['global']['subsystems']:
            myclass = getattr(__import__(subsystem), subsystem)
            mysubsystem = myclass(self.MCP_path)
            myfunction = getattr(mysubsystem, "update_status")
            myfunction("")

        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : " + self.subsystem + " started'" ])

    def stop(self, params):
        function = 'stop'
        desc = "description: this function deletes the files of the control API"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to stop " + self.subsystem + "'" ])
        self.run_action("stop_control_api", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : " + self.subsystem + " stopped'" ])

    def restart(self, params):
        function = 'restart'
        desc = "description: this function deletes then writes the default files for the control API"
        self.parse_function_params(function, [], {}, desc, params)

        self.stop(params)
        self.start(params)
