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
import inspect
import os
import getpass
import warnings
from ConfigParser import ConfigParser

MLOG_CONF_FILE_DEFAULT = "/etc/mlog/mlog.conf"
MLOG_ENV_FILE = 'MLOG_CONFIG_FILE'
GLOBAL = 'global'
MLOG_LOG_LEVEL = 'mlog_log_level'
MLOG_API_URL = 'mlog_api_url'
MLOG_LOG_FILE = 'mlog_log_file'

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
#ALLOWED_LOG_LEVELS = set(MLOG_TEXT_TO_LEVEL.values())
MLOG_LEVEL_TO_TEXT = {}
for k, v in MLOG_TEXT_TO_LEVEL.iteritems():
    MLOG_LEVEL_TO_TEXT[v] = k
LOG_LEVEL_MIN = min(MLOG_LEVEL_TO_TEXT.keys())
LOG_LEVEL_MAX = max(MLOG_LEVEL_TO_TEXT.keys())


class mlog(object):
    """
    This class contains the methods necessary for sending log messages.
    """

    def __init__(self, subsystem, constraints=None, config=None):
        if not subsystem:
            raise ValueError("Subsystem must be supplied")

        self.subsystem = subsystem
        self.user_log_level = -1
        self.config_log_level = -1
        self.config_log_file = config
        if not config:
            self.config_log_file = os.environ.get(MLOG_ENV_FILE, None)
        if not config:
            self.config_log_file = MLOG_CONF_FILE_DEFAULT
        self.msg_count = 0
        self.recheck_api_msg = 100
        self.recheck_api_time = 300  # 5 mins
        self.log_constraints = {} if not constraints else constraints

        self.update_config()

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

    def _get_config_items(self, cfg, section):
        cfgitems = {}
        if cfg.has_section(section):
            for k, v in cfg.items(section):
                cfgitems[k] = v
        return cfgitems

    def update_config(self):
        self.api_log_level = -1
        self.msgs_since_api_update = 0
        self.time_since_api_update = datetime.datetime.now()

        api_url = None
        print self.config_log_file
        if os.path.isfile(self.config_log_file):
            cfg = ConfigParser()
            cfg.read(self.config_log_file)
            cfgitems = self._get_config_items(cfg, GLOBAL)
            cfgitems.update(self._get_config_items(cfg, self.subsystem))
            if MLOG_LOG_LEVEL in cfgitems:
                self.config_log_level = cfgitems[MLOG_LOG_LEVEL]
            if MLOG_API_URL in cfgitems:
                api_url = cfgitems[MLOG_API_URL]
            if MLOG_LOG_FILE in cfgitems:
                self.config_log_file = cfgitems[MLOG_LOG_FILE]
        # Retrieving the control API defined log level
#        for line in open(MLOG_CONF_FILE):
#            line.strip()
#            if(re.match(r'^url\s+', line)):
#                api_url = line.split()[1]

        if(api_url):
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
        elif(level not in MLOG_LEVEL_TO_TEXT):
            raise ValueError('Illegal log level')
        return level

    def set_log_level(self, level):
        self.user_log_level = self._get_log_level(level)

    def set_log_msg_check_count(self, count):
        count = int(count)
        if count < 0:
            raise ValueError('Cannot check a negative number of messages')
        self.recheck_api_msg = count

    def set_log_msg_check_interval(self, interval):
        interval = int(interval)
        if interval < 0:
            raise ValueError('interval must be positive')
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
