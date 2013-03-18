#!/soft/packages/python/2.6/bin/python

import sys

# Adding modules directory to path
path = list(sys.path)
sys.path.insert(0, ".")

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
