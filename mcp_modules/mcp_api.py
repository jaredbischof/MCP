import glob, json, os, sys, time
from subsystem import subsystem

class mcp_api(subsystem):
    actions = "start, stop, restart"

    def __init__(self, MCP_dir):
        subsystem.__init__(self, MCP_dir)
        self.state = { 'resource':self.__class__.__name__,
                       'updated':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       'url':self.json_conf['global']['apiurl'] + "/" + str(self.json_conf['mcp_api']['version']) + "/" + self.__class__.__name__,
                       'status':'online'
                     }
        self.apidir = self.json_conf['mcp_api']['dir'] + "/" + str(self.json_conf['mcp_api']['version'])
        self.services = self.json_conf['global']['services']

    def start(self):
        files = glob.glob(self.apidir+"/*")
        if len(files) != 0:
            sys.stderr.write("ERROR: Cannot initialize mcp_api because API directory (" + self.apidir + ") is not empty\n")
            return 0

        for service in self.services:
            service = service.strip();
            module = __import__(service)
            myclass = getattr(module, service)
            myservice = myclass(self.MCP_dir)

            jstate = json.dumps(myservice.get_state())
            f = open(self.apidir + "/" + service, 'w')
            f.write(jstate)

    def stop(self):
        for file_object in os.listdir(self.apidir):
            file_object_path = os.path.join(self.apidir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    def restart(self):
        self.stop()
        self.start()
