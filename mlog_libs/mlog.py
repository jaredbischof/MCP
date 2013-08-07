"""
NAME
       mlog

DESCRIPTION
       A library for sending logging messages to syslog.

METHODS
       mlog(string subsystem, hashref constraints): Initializes mlog. You
           should call this at the beginning of your program. Constraints are
           optional.

       logit(int level, string message): sends log message to syslog.

       *         level: (0-9) The logging level for this message is compared to
                    the logging level that has been set in mlog.  If it is <=
                    the set logging level, the message will be sent to syslog,
                    otherwise it will be ignored.  Logging level is set to 6
                    if control API cannot be reached and the user does
                    not set the log level. Log level can also be entered as
                    string (e.g. 'DEBUG')

       *          message: This is the log message.

       get_log_level(): Returns the current log level as an integer.

       set_log_level(integer level) : Sets the log level. Only use this if you
           wish to override the log levels that are defined by the control API.
           Can also be entered as string (e.g. 'DEBUG')

       *          level : priority

       *          0 : EMERG - system is unusable

       *          1 : ALERT - component must be fixed immediately

       *          2 : CRIT - secondary component must be fixed immediately

       *          3 : ERR - non-urgent failure

       *          4 : WARNING - warning that an error will occur if no action
                                is taken

       *          5 : NOTICE - unusual but safe conditions

       *          6 : INFO - normal operational messages

       *          7 : DEBUG - lowest level of debug

       *          8 : DEBUG2 - second level of debug

       *          9 : DEBUG3 - highest level of debug

       set_log_msg_check_count(integer count): used to set the number the
           messages that mlog will log before querying the control API for the
           log level (default is 100 messages).

       set_log_msg_check_interval(integer seconds): used to set the interval,
           in seconds, that will be allowed to pass before mlog will query the
           control API for the log level (default is 300 seconds).

       update_api_log_level() : Checks the control API for the currently set
           log level.

       use_api_log_level() : Removes the user-defined log level and tells mlog
           to use the control API-defined log level.
"""

import json
import urllib2
import syslog
import datetime
import re
import inspect
import os
import getpass
import warnings

MLOG_CONF_FILE = "/etc/mlog/mlog.conf"
DEFAULT_LOG_LEVEL = 6
#MSG_CHECK_COUNT = 100
#MSG_CHECK_INTERVAL = 300  # 300s = 5min
MSG_FACILITY = syslog.LOG_LOCAL1
EMERG_FACILITY = syslog.LOG_LOCAL0
MLOG_TEXT_TO_LEVEL = {'EMERG': 0,
                      'ALERT': 1,
                      'CRIT': 2,
                      'ERR': 3,
                      'WARNING': 4,
                      'NOTICE': 5,
                      'INFO': 6,
                      'DEBUG': 7,
                      'DEBUG2': 8,
                      'DEBUG3': 9,
                      }
MLOG_TO_SYSLOG = [syslog.LOG_EMERG, syslog.LOG_ALERT, syslog.LOG_CRIT,
                 syslog.LOG_ERR, syslog.LOG_WARNING, syslog.LOG_NOTICE,
                 syslog.LOG_INFO, syslog.LOG_DEBUG, syslog.LOG_DEBUG,
                 syslog.LOG_DEBUG]
ALLOWED_LOG_LEVELS = set(MLOG_TEXT_TO_LEVEL.value())
LOG_LEVEL_MIN = min(ALLOWED_LOG_LEVELS)
LOG_LEVEL_MAX = max(ALLOWED_LOG_LEVELS)
MLOG_LEVEL_TO_TEXT = {}
for k, v in MLOG_TEXT_TO_LEVEL.iteritems():
    MLOG_LEVEL_TO_TEXT[v] = k


class mlog(object):
    """
    This class contains the methods necessary for sending log messages.
    """

    def __init__(self, subsystem, constraints=None):
        if not subsystem:
            raise ValueError("Subsystem must be supplied")

        self.subsystem = subsystem
        self.user_log_level = -1
        self.msg_count = 0
        self.recheck_api_msg = 100
        self.recheck_api_time = 300  # 5 mins
        self.log_constraints = {} if not constraints else constraints

        self.update_api_log_level()

    def _get_time_since_start(self):
        time_diff = datetime.datetime.now() - self.time_since_api_update
        return (time_diff.days * 24 * 60 * 60) + time_diff.seconds

    def get_log_level(self):
        if(self.user_log_level != -1):
            return self.user_log_level
        elif(self.api_log_level != -1):
            return self.api_log_level
        else:
            return DEFAULT_LOG_LEVEL

    def update_api_log_level(self):
        self.api_log_level = -1
        self.msgs_since_api_update = 0
        self.time_since_api_update = datetime.datetime.now()

        # Retrieving the control API defined log level
        api_url = ""
        for line in open(MLOG_CONF_FILE):
            line.strip()
            if(re.match(r'^url\s+', line)):
                api_url = line.split()[1]

        if(api_url != ""):
            subsystem_api_url = api_url + "/" + self.subsystem
            try:
                data = json.load(urllib2.urlopen(subsystem_api_url, timeout=5))
            except urllib2.URLError, e:
                code_ = None
                if hasattr(e, 'code'):
                    code_ = ' ' + str(e.code)
                warnings.warn(
                    'Could not connect to mlog api server at ' +
                    '{}:{} {}. Using default log level {}.'.format(
                    subsystem_api_url, code_, str(e.reason),
                    str(DEFAULT_LOG_LEVEL)))
#                sys.stderr.write(e.code + "\n")
#            except urllib2.URLError, e:
#                sys.stderr.write("WARNING: Could not access control API at '"
#                                 + subsystem_api_url + "'\n")
#                sys.stderr.write("           due to urllib2 error '"
#                                 + str(e.args) + "'\n")
#                sys.stderr.write("         Will instead use default log level of '"
#                                 + str(DEFAULT_LOG_LEVEL) + "'\n")
            else:
                max_matching_level = -1
                for constraint_set in data['log_levels']:
                    level = constraint_set['level']
                    constraints = constraint_set['constraints']
                    if level <= max_matching_level:
                        continue

                    matches = 1
                    for constraint in constraints:
                        if constraint not in self.log_constraints:
                            matches = 0
                        elif (self.log_constraints[constraint] !=
                              constraints[constraint]):
                            matches = 0

                    if matches == 1:
                        max_matching_level = level

                self.api_log_level = max_matching_level

    def _get_log_level(self, level):
        if(level in MLOG_TEXT_TO_LEVEL):
            level = MLOG_TEXT_TO_LEVEL[level]
        elif(level not in ALLOWED_LOG_LEVELS):
            raise ValueError('Illegal log level')
        return level

    def set_log_level(self, level):
        self.user_log_level = self._get_log_level(level)

    def set_log_msg_check_count(self, count):
        count = int(count)
        if count < 0:
            raise ValueError('Cannot check a negative number of messages')
#        if(not isinstance(count, int)):
#            sys.stderr.write("ERROR: Format for calling set_log_msg_check_count is set_log_msg_check_count(integer count)\n")
#            return 1
        self.recheck_api_msg = count

    def set_log_msg_check_interval(self, interval):
        interval = int(interval)
        if interval < 0:
            raise ValueError('interval must be positive')
#        if(not isinstance(interval, int)):
#            sys.stderr.write("ERROR: Format for calling set_log_msg_check_interval is set_log_msg_check_interval(integer seconds)\n")
#            return 1
        self.recheck_api_time = interval

    def use_api_log_level(self):
        self.user_log_level = -1

    def _syslog(self, facility, level, user, file_, message):
        syslog.openlog("[" + self.subsystem + "] [" + MLOG_LEVEL_TO_TEXT[level]
                       + "] [" + user + "] [" + file_ + "] ",
                       syslog.LOG_PID, facility)
        syslog.syslog(MLOG_TO_SYSLOG[level], message)
        syslog.closelog()

    def logit(self, level, message):
        message = str(message)
        level = self._get_log_level(level)

        self.msg_count += 1
        self.msgs_since_api_update += 1

        user = getpass.getuser()
        file_ = os.path.abspath(inspect.getfile(inspect.stack()[1][0]))

        if(self.msgs_since_api_update >= self.recheck_api_msg
           or self._get_time_since_start() >= self.recheck_api_time):
            self.update_api_log_level()

        # If this message is an emergency, send a copy to the emergency
        # facility first.
        if(level == 0):
            self._syslog(EMERG_FACILITY, level, user, file_, message)

        if(level <= self.get_log_level()):
            self._syslog(MSG_FACILITY, level, user, file_, message)

if __name__ == '__main__':
    pass
