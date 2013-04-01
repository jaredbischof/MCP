from subsystem import subsystem

class upload(subsystem):
    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)

    def update_status(self, params):
        function = 'update_status'
        desc = "description: this function updates the status of the upload subsystem in the control api"
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to update the upload subsystem api status'" ])
        self.run_action("update_upload_status", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : upload subsystem api status updated'" ])

    def lock_page(self, params):
        function = 'lock_page'
        desc = "description: this function creates the lock file for the MG-RAST production upload page and thus disables that page."
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to lock the upload page'" ])
        self.run_action("lock_upload_page", self.get_req_login(function), [])
        self.run_action("update_upload_status", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : upload page locked and upload subsystem api status updated'" ])

    def unlock_page(self, params):
        function = 'unlock_page'
        desc = "description: this function deletes the lock file for the MG-RAST production upload page and thus enables that page."
        self.parse_function_params(function, [], {}, desc, params)

        self.run_action("log_msg", "ANY", [ "INFO", "'REQUEST : attempting to unlock the upload page'" ])
        self.run_action("unlock_upload_page", self.get_req_login(function), [])
        self.run_action("update_upload_status", self.get_req_login(function), [])
        self.run_action("log_msg", "ANY", [ "INFO", "'SUCCESS : upload page unlocked and upload subsystem api status updated'" ])
