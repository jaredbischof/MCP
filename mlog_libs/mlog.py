"""
NAME
       mlog

DESCRIPTION
       A library for sending MG-RAST logging to syslog.

METHODS
       logit(level, component, message, error_code): sends mgrast log message to syslog.

       *         level: (0-6) The logging level for this message is compared to the logging level that has been set in
                 mlog.  If it is <= the set logging level, the message will be sent to syslog, otherwise it will be
                 ignored.  Logging level is set to 6 if MG-RAST control API cannot be reached.

       *         component: (string) This is the utility within MG-RAST that is logging the message.  This is a free
                 text field.

       *         message: (string) This is the log message.

       *         error_code: (string) The error code for this log message.

       set_log_level(integer level, string component) : Sets the logging level of the given component. Only use this if
       you wish to override the log levels that are defined by the control API.

       *         level : priority

       *         0 : emergencies - vital component is down

       *         1 : alerts - non-vital component is down

       *         2 : errors - error that prevents proper operation

       *         3 : warning - error, but does not prevent operation

       *         4 : debug - lowest level of debug

       *         5 : debug2 - second level of debug

       *         6 : debug3 - highest level of debug

       set_log_msg_check_count(integer count): used to set the number the messages that mlog will log before querying
       the control API for the log level of all components (default is 100 messages).

       set_log_msg_check_interval(integer seconds): used to set the interval, in seconds, that will be allowed to pass
       before  mlog will  query the control API for the log level of the given component (default is 300 seconds).

       use_all_api_log_levels() : Removes all user-defined log levels and tells mlog to use the control API defined log
       levels.

       use_api_log_level(string component) : Removes the user-defined log level for this component and tells mlog to use
       the control API defined log levels.

"""

import json
import urllib2
import syslog
import datetime, re
import inspect, os, getpass, sys

MLOG_CONF_FILE = "/etc/mlog/mlog.conf"
DEFAULT_LOG_LEVEL = 6
MSG_CHECK_COUNT = 100
MSG_CHECK_INTERVAL = 300 # 300s = 5min
MSG_FACILITY = syslog.LOG_LOCAL1
EMERG_FACILITY = syslog.LOG_LOCAL0
LOG_LEVEL_TEXT = [ syslog.LOG_EMERG, syslog.LOG_ALERT, syslog.LOG_CRIT, syslog.LOG_ERR,
                   syslog.LOG_WARNING, syslog.LOG_NOTICE, syslog.LOG_INFO, syslog.LOG_DEBUG ]

class mlog(object):
    """
    This class contains the methods necessary for sending MG-RAST log messages.
    """

    def __init__(self):
        self.user_defined_log_levels = {}
        self.msg_count = 0
        self._update_api_defined_log_levels()

    def _update_api_defined_log_levels(self):
        self.api_defined_log_levels = {}
        self.last_update_msg_count = 0
        self.last_update_time = datetime.datetime.now()

        # Retrieving the control API defined log levels...
        api_mlog_url = ""
        for line in open(MLOG_CONF_FILE):
            line.strip()
            if(re.match(r'^url\s+', line)):
                api_mlog_url = line.split()[1]

        if(api_mlog_url != ""):
            try:
                data = json.load(urllib2.urlopen(api_mlog_url, timeout = 5))
            except urllib2.HTTPError, e:
                print e.code
            except urllib2.URLError, e:
                print "WARNING: Could not access control API at '"+api_mlog_url+"'"
                print "           due to urllib2 error '"+str(e.args)+"'"
                print "         Will instead use default log level of '"+str(DEFAULT_LOG_LEVEL)+"' for all components."
                print "         Alternatively, you can set log levels for components with mlog using:"
                print "         set_log_level(integer level, string component)"
            else:
                for component in data['log_levels']:
                    self.api_defined_log_levels[component] = data['log_levels'][component]

    def _get_log_level(self, component):
        if(component in self.user_defined_log_levels):
            return self.user_defined_log_levels[component]
        elif(component in self.api_defined_log_levels):
            return self.api_defined_log_levels[component]
        else:
            return DEFAULT_LOG_LEVEL

    def _get_time_since_start(self):
        time_diff = datetime.datetime.now() - self.last_update_time
        return ( (time_diff.days * 24 * 60 * 60) + time_diff.seconds )

    def set_log_level(self, level, component):
        if(not isinstance(level, int) or component == ""):
            sys.stderr.write("ERROR: Format for calling set_log_level is set_log_level(integer level, string component)\n")
            return 0
        self.user_defined_log_levels[component] = level
        return 1

    def set_log_msg_check_count(self, count):
        if(not isinstance(count, int)):
            sys.stderr.write("ERROR: Format for calling set_log_msg_check_count is set_log_msg_check_count(integer count)\n")
            return 0
        MSG_CHECK_COUNT = count
        return 1

    def set_log_msg_check_interval(self, interval):
        if(not isinstance(interval, int)):
            sys.stderr.write("ERROR: Format for calling set_log_msg_check_interval is set_log_msg_check_interval(integer seconds)\n")
            return 0
        MSG_CHECK_INTERVAL = interval
        return 1

    def use_all_api_log_levels(self):
        self.user_defined_log_levels.clear()
        return 1

    def use_api_log_level(self, component):
        if(component == ""):
            sys.stderr.write("ERROR: Format for calling use_api_log_level is use_api_log_level(string component)\n")
            return 0
        del self.user_defined_log_levels[component]
        return 1

    def logit(self, level, component, message, error_code):
        if(not isinstance(level, int) or component == ""):
            sys.stderr.write("ERROR: Format for calling logit is logit(integer level, string component, string message, string error_code)\n")
            return 0

        if(level < 0 or level > 6):
            sys.stderr.write("ERROR: mlog level '"+level+"' is invalid, you must enter an integer between 0 and 6, inclusive.\n")
            return 0

        ++self.msg_count
        ++self.last_update_msg_count

        user = getpass.getuser()
        ident = os.path.abspath(inspect.getfile(inspect.stack()[1][0]))
        logopt = ""

        if(self.last_update_msg_count >= MSG_CHECK_COUNT or self._get_time_since_start() >= MSG_CHECK_INTERVAL):
            self._update_api_defined_log_levels()

        # If this message is an emergency, send a copy to the emergency facility first.
        if(level == 0):
            syslog.openlog(component+":"+user+":"+error_code+":"+ident, syslog.LOG_PID, EMERG_FACILITY)
            syslog.syslog(syslog.LOG_EMERG, message)
            syslog.closelog()

        if(level <= self._get_log_level(component)):
            syslog.openlog(component+":"+user+":"+error_code+":"+ident, syslog.LOG_PID, MSG_FACILITY)
            syslog.syslog(LOG_LEVEL_TEXT[level], message)
            syslog.closelog()
        else:
            return 0

        return 1
