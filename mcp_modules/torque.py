from subsystem import subsystem

class torque(subsystem):
    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

    def update_status(self, params):
        function = 'update_status'
        desc = "description: this function updates the status of the torque subsystem in the control API"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to update the torque subsystem api status'" ])
        self.run_action("update_torque_status", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : torque subsystem api status updated'" ])

    def start_batch(self, params):
        function = 'start_batch'
        desc = "description: this function starts the batch torque queue"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to start the batch torque queue'" ])
        self.run_action("start_batch_queue", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : batch torque queue started'" ])

    def stop_batch(self, params):
        function = 'stop_batch'
        desc = "description: this function stops the batch torque queue"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to stop the batch torque queue'" ])
        self.run_action("stop_batch_queue", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : batch torque queue stopped'" ])

    def start_fast(self, params):
        function = 'start_fast'
        desc = "description: this function starts the fast torque queue"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to start the fast torque queue'" ])
        self.run_action("start_fast_queue", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : fast torque queue started'" ])

    def stop_fast(self, params):
        function = 'stop_fast'
        desc = "description: this function stops the fast torque queue"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to stop the fast torque queue'" ])
        self.run_action("stop_fast_queue", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : fast torque queue stopped'" ])
