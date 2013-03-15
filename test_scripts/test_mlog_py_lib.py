#!/soft/packages/python/2.6/bin/python

import os
import sys
import re, time

# Getting paths
MCP_path = os.path.realpath(__file__)
matchObj = re.match(r'(^.*\/)', MCP_path)
MCP_dir = matchObj.group(0)

# Adding modules directory to path
path = list(sys.path)
sys.path.insert(0, MCP_dir+"mlog_libs/")

from mlog import mlog

m = mlog()
if(m.logit(5, 'mgrast', 'my test message', 'error code X')):
    print "log message sent!"
else:
    print "log message not sent."

if(m.set_log_level(5, "mgrast")):
  print "log level changed!";
else:
  print "log level not changed.";

if(m.logit(5, "mgrast", "test_msg", "error code Y")):
  print "log message sent!"
else:
  print "log message not sent."
