import json, sys
from subsystem import subsystem

class mlog(subsystem):
    actions = [ 'log' ]

    def __init__(self, MCP_path):
        subsystem.__init__(self, MCP_path)
