import sys, glob
from mcp_base import mcp_base

class mcp_api(mcp_base):
    actions = "init"

    def init(self):
        """Initializes MCP API"""
        files = glob.glob(self.apidir+"/*")
        if len(files) != 0:
            sys.stderr.write("ERROR: Cannot initialize mcp_api because API directory (" + self.apidir + ") is not empty\n")
            return
