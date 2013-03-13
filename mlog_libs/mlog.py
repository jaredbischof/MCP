"""
NAME
       mlog

DESCRIPTION
       A library for sending MG-RAST logging to syslog.

METHODS
       init_mlog(): Initializes mlog. It's good to call this at the beginning of your program.

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

import datetime, re

#__all__ = ["mlog", "set_log_level", "set_log_msg_check_count", "set_log_msg_check_interval", "logit", "use_all_api_log_levels", "use_api_log_level"]

MLOG_CONF_FILE = "/etc/mlog/mlog.conf"
DEFAULT_LOG_LEVEL = 6
MSG_CHECK_COUNT = 100
MSG_CHECK_INTERVAL = 300 # 300s = 5min
LOG_LEVEL_TEXT = [ 'emerg', 'alert', 'crit', 'err',
                   'warning', 'notice', 'info', 'debug' ]

api_defined_log_levels = {}
user_defined_log_levels = {}
msg_count = 0
last_update_time = ""
last_update_msg_count = 0

class mlog():
    """
    This class contains the methods necessary for sending MG-RAST log messages.
    """

    def __init__(self):
        self.last_update_msg_count = 0
        self.last_update_time = datetime.datetime.now()

        api_mlog_url = ""
        for line in open(MLOG_CONF_FILE):
            line.strip()
            if(re.match(r'^url\s+', line)):
                api_mlog_url = line.split()[1]

        if(api_mlog_url != ""):
            import json
            import urllib2

            data = json.load(urllib2.urlopen(api_mlog_url))
            for components in data['components']:
                api_defined_log_levels[components['name']] = components['log_level']

    def _get_log_level(self, component):
        if(component in api_defined_log_levels):
            return api_defined_log_levels[component]
        elif(component in user_defined_log_levels):
            return user_defined_log_levels[component]
        else:
            return DEFAULT_LOG_LEVEL
