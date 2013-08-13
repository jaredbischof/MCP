package mlog;

@ISA = qw(Exporter);
@EXPORT = qw(init_mlog get_log_level update_config set_log_level set_log_file set_log_msg_check_count set_log_msg_check_interval clear_user_log_level logit);

use strict;
use warnings;
use Config::Simple;
use LWP::Simple;
use JSON qw( decode_json );
use DateTime;
use Cwd 'abs_path';
use Data::Dumper;
use Sys::Hostname;
use List::Util qw[min max];

use Sys::Syslog qw( :DEFAULT setlogsock);

require Exporter;

# $ENV{'MLOG_CONFIG_FILE'} should point to an INI-formatted file, or an empty string, or should not exist.
my $MLOG_CONFIG_FILE_DEFAULT = "/etc/mlog/mlog.conf";
my $MLOG_ENV_FILE = "MLOG_CONFIG_FILE";
my $_GLOBAL = "global";
my $MLOG_LOG_LEVEL = "mlog_log_level";
my $MLOG_API_URL = "mlog_api_url";
my $MLOG_LOG_FILE = "mlog_log_file";

my $DEFAULT_LOG_LEVEL = 6;
#my $MSG_CHECK_COUNT = 100;
#my $MSG_CHECK_INTERVAL = 300; # 300s = 5min
my $MSG_FACILITY = 'local1';
my $EMERG_FACILITY = 'local0';

my $EMERG = 0;
my $ALERT = 1;
my $CRIT = 2;
my $ERR = 3;
my $WARNING = 4;
my $NOTICE = 5;
my $INFO = 6;
my $DEBUG = 7;
my $DEBUG2 = 8;
my $DEBUG3 = 9;

my $_MLOG_TEXT_TO_LEVEL = { 'EMERG' => $EMERG,
							'ALERT' => $ALERT,
							'CRIT' => $CRIT,
							'ERR' => $ERR,
							'WARNING' => $WARNING,
							'NOTICE' => $NOTICE,
							'INFO' => $INFO,
							'DEBUG' => $DEBUG,
							'DEBUG2' => $DEBUG2,
							'DEBUG3' => $DEBUG3,
							};

my @_MLOG_TO_SYSLOG = (0, 1, 2, 3, 4, 5, 6, 7, 7, 7);

my $_MLOG_LEVEL_TO_TEXT = {};
foreach my $k ($_MLOG_TEXT_TO_LEVEL->keys()) {
	$_MLOG_LEVEL_TO_TEXT->{$_MLOG_TEXT_TO_LEVEL->{$k}} = $k;
}

my $LOG_LEVEL_MIN = min($_MLOG_LEVEL_TO_TEXT->keys());
my $LOG_LEVEL_MAX = max($_MLOG_LEVEL_TO_TEXT->keys());

#my @SYSLOG_LEVEL_TEXT  = ( 'emerg', 'alert', 'crit', 'err',
#                           'warning', 'notice', 'info', 'debug' );
#my %MLOG_TEXT_TO_LEVEL = ( 'EMERGENCY' => 0,
#                           'ERROR' => 1,
#                           'WARNING' => 2,
#                           'INFO' => 3,
#                           'DEBUG' => 4,
#                           'DEBUG2' => 5,
#                           'DEBUG3' => 6 );
#my @MLOG_LEVELS = ( 'EMERGENCY', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'DEBUG2', 'DEBUG3' );

#my $SUBSYSTEM = "";
#my $API_LOG_LEVEL = -1;
#my $USER_LOG_LEVEL = -1;
#my $USER_LOG_FILE = "";
#my $CONFIG_LOG_LEVEL = -1;
#my $CONFIG_LOG_FILE = "";
#my $LOG_CONSTRAINTS;
#my $MSG_COUNT = 0;
#my $TIME_AT_LAST_CONFIG_UPDATE = "";
#my $MSGS_SINCE_LAST_CONFIG_UPDATE = 0;

=pod

=head1 NAME

mlog (message log)

=head1 DESCRIPTION

A library for sending message logging to syslog.

The library checks for the config variables: mlog_log_level, mlog_api_url, and mlog_log_file in an INI-formatted config file that can be specified by setting the environment variable MLOG_CONFIG_FILE. The library first looks for these variables under a 'section' in the INI file which matches the 'subsystem' name in mlog->new() call. mlog_log_level can be used to set a global log level for mlog. mlog_api_url can be set to provide a control API for setting log levels. mlog_log_file can be set to provide the location of a file to which we can log messages in addition to syslog.

The priority that is used to decide which log level setting is used for logging is as follows:

=over 10

=item * USER_LOG_LEVEL: log level set within the program that is using mlog by calling set_log_level()

=item * CONFIG_LOG_LEVEL: log level (mlog_log_level) set within the INI file located at the path set in $ENV{'MLOG_CONFIG_FILE'}

=item * API_LOG_LEVEL: log level set by the logging control server in the control API matching the log constraints (if mlog_api_url is specified in config file)

=item * DEFAULT_LOG_LEVEL: INFO, log level = 6

=back

=head1 METHODS

mlog->new(string subsystem, hashref constraints): Create a new mlog instance. Constraints are optional.

logit(int level, string message): sends log message to syslog.

=over 10

=item * level: (0-9) The logging level for this message is compared to the logging level that has been set in mlog.  If it is <= the set logging level, the message will be sent to syslog (and if specified in the mlog configuration, a log file), otherwise it will be ignored.  Logging level is set to 6 if message control API cannot be reached and the user does not set the log level. Log level can also be entered as string (e.g. 'DEBUG')

=item * message: This is the log message.

=back

get_log_level(): Returns the current log level as an integer.

set_log_level(integer level) : Sets the log level. Only use this if you wish to override the log levels that are defined by the mlog configuration file and the control API. Can also be entered as string (e.g. 'DEBUG')

=over 10

=item * level : priority

=item * 0 : EMERG - system is unusable

=item * 1 : ALERT - component must be fixed immediately

=item * 2 : CRIT - secondary component must be fixed immediately

=item * 3 : ERR - non-urgent failure

=item * 4 : WARNING - warning that an error will occur if no action is taken

=item * 5 : NOTICE - unusual but safe conditions

=item * 6 : INFO - normal operational messages

=item * 7 : DEBUG - lowest level of debug

=item * 8 : DEBUG2 - second level of debug

=item * 9 : DEBUG3 - highest level of debug

=back

set_log_file(string filename): Used to set or update the path to the file where we would like to have messages logged. Log file set in program with this function will over-ride any log file set in the config file.

set_log_msg_check_count(integer count): Used to set the number the messages that mlog will log before checking the mlog configuration and querying the control API for the log level if mlog_api_url is set in $ENV{'MLOG_CONFIG_FILE'} (default is 100 messages).

set_log_msg_check_interval(integer seconds): Used to set the interval, in seconds, that will be allowed to pass before mlog will check the mlog configuration and query the control API for the log level if mlog_api_url is set in $ENV{'MLOG_CONFIG_FILE'} (default is 300 seconds).

update_config() : Checks the mlog configuration file at $ENV{'MLOG_CONFIG_FILE'} for mlog_log_level, mlog_api_url, and mlog_log_file and checks the control API for the currently set log level if mlog_api_url is set.

clear_user_log_level() : Removes the user-defined log level.

=cut

sub _get_option {
    my ($opts, $key) = @_;
    if(!(defined $opts)) {
        return undef;
    }
    return defined $opts->{$key} ? $opts->{$key} : undef;
}

sub new {
    my ($class, $sub, $lc, $options) = @_;
    unless(defined $sub) {
        die "ERROR: You must define a subsystem when calling init_log()\n";
    }
    my $self = {
    };
    bless $self, $class;
    $self->{authuser} = _get_option($options, 'authuser');
    $self->{module} = _get_option($options, 'module');
    $self->{method} = _get_option($options, 'method');
    $self->{call_id} = _get_option($options, 'call_id');
    $self->{_callback} = defined $options->{"changecallback"} ? 
            $options->{"changecallback"} : sub {};
    $self->{_subsystem} = $sub;
    $self->{_mlog_config_file} = _get_option($options, 'config');
    if(!(defined $self->{_mlog_config_file})) {
        $self->{_mlog_config_file} = defined $ENV{$MLOG_ENV_FILE} ?
                $ENV{$MLOG_ENV_FILE} : undef;
    }
    if(!(defined $self->{_mlog_config_file})) {
        $self->{_mlog_config_file} = $MLOG_CONFIG_FILE_DEFAULT;
    }
    $self->{_user_log_level} = -1;
    $self->{_config_log_level} = -1;
    $self->{_user_log_file} = _get_option($options, 'logfile');
    $self->{_config_log_file} = undef;
    $self->{_api_log_level} = -1;
    $self->{_msgs_since_config_update} = 0;
    $self->{_time_at_config_update} = "";
    $self->{msg_count} = 0;
    $self->{_recheck_api_msg} = 100;
    $self->{_recheck_api_time} = 300;  # 5 mins
    if(defined $lc) {
        $self->{_log_constraints} = $lc;
    }
#    $USER_LOG_LEVEL = -1;
#    $CONFIG_LOG_LEVEL = -1;
#    $CONFIG_LOG_FILE = "";
#    $MSG_COUNT = 0;
#
#    if(exists $ENV{'MLOG_CONFIG_FILE'}) {
#        $MLOG_CONFIG_FILE = $ENV{'MLOG_CONFIG_FILE'};
#    }
    $self->{_init} = 1;
    $self->update_config();
    $self->{_init} = undef;
}

sub _get_time_since_start {
    my ($self) = @_;
    my $now = DateTime->now( time_zone => 'local' )->set_time_zone('floating');
    my $seconds_duration = $now->subtract_datetime_absolute($self->{_time_at_config_update});
    return $seconds_duration->seconds;
}

sub get_log_level {
    my ($self) = @_;
    if($self->{_user_log_level} != -1) {
        return $self->{_user_log_level};
    } elsif($self->{_config_log_level} != -1) {
        return $self->{_config_log_level};
    } elsif($self->{_api_log_level} != -1) {
        return $self->{_api_log_level};
    } else {
        return $DEFAULT_LOG_LEVEL;
    }
}

sub update_config {
    my ($self) = @_;
    my $loglevel = $self->get_log_level();
    my $logfile = $self->get_log_file();
    
    $self->{_api_log_level} = -1;
    $self->{_msgs_since_config_update} = 0;
    $self->{_time_at_config_update} = DateTime->now( time_zone => 'local' )->set_time_zone('floating');
    
#    $API_LOG_LEVEL = -1;
#    $MSGS_SINCE_LAST_CONFIG_UPDATE = 0;
#    $TIME_AT_LAST_CONFIG_UPDATE = DateTime->now( time_zone => 'local' )->set_time_zone('floating');

    # Retrieving config variables.
    my $api_url = "";
    if(-e $self->{_mlog_config_file} && -s $self->{_mlog_config_file} > 0) {
        my $cfg = new Config::Simple($self->{_mlog_config_file});
        my $cfgitems = $cfg->get_block($_GLOBAL);
        my $subitems = $cfg->get_block($self->{_subsystem});
        my %cfg = %{$cfg};
        @cfg{keys %{$subitems}} = values %{$subitems};
        if(defined $cfg->{$MLOG_LOG_LEVEL}) {
            if($cfg->{$MLOG_LOG_LEVEL} !~ /^\d+$/) {
                warn "Cannot parse log level $cfg->{$MLOG_LOG_LEVEL} from " + 
                    "file $self->{_mlog_config_file} to int. Keeping " +
                    "current log level.";
            } else {
                $self->{_config_log_level} = $cfg->{$MLOG_LOG_LEVEL};
            }
        }
        if(defined $cfg->{$MLOG_API_URL}) {
            $api_url = $cfg->{$MLOG_API_URL};
        }
        if(defined $cfg->{$MLOG_LOG_FILE}) {
            $self->{_config_log_file} = $cfg->{$MLOG_LOG_FILE}
        }
#        if(exists $subsys_hash->{'mlog_log_level'}) {
#            $CONFIG_LOG_LEVEL = $subsys_hash->{'mlog_log_level'};
#        } elsif(exists $global_hash->{'mlog_log_level'}) {
#            $CONFIG_LOG_LEVEL = $global_hash->{'mlog_log_level'};
#        }
#                
#        if(exists $subsys_hash->{'mlog_api_url'}) {
#            $api_url = $subsys_hash->{'mlog_api_url'};
#        } elsif(exists $global_hash->{'mlog_api_url'}) {
#            $api_url = $global_hash->{'mlog_api_url'};
#        }
#
#        if(exists $subsys_hash->{'mlog_log_file'}) {
#            $CONFIG_LOG_FILE = $subsys_hash->{'mlog_log_file'};
#        } elsif(exists $global_hash->{'mlog_log_file'}) {
#            $CONFIG_LOG_FILE = $global_hash->{'mlog_log_file'};
#        }
    } elsif (defined $self->{_mlog_config_file}) {
        warn "Cannot read config file $self->{_mlog_config_file}";
    }

    unless($api_url eq "") {
        my $subsystem_api_url = $api_url."/$self->{_subsystem}";
        my $json = get($subsystem_api_url);
        if(defined $json) {
            my $decoded_json = decode_json($json);
            my $max_matching_level = -1;
            foreach my $constraint_set (@{$decoded_json->{'log_levels'}}) {
                my $level = $constraint_set->{'level'};
                my $constraints = $constraint_set->{'constraints'};
                if($level <= $max_matching_level) {
                    next;
                }
                my $matches = 1;
                foreach my $constraint (keys %{$constraints}) {
                    if(! exists $self->{_log_constraints}->{$constraint}) {
                        $matches = 0;
                    } elsif($self->{_log_constraints}->{$constraint} ne $constraints->{$constraint}) {
                        $matches = 0;
                    }
                }
                if($matches == 1) {
                    $max_matching_level = $level;
                }
            }
            $self->{_api_log_level} = $max_matching_level;
        } else {
            warn "Could not retrieve mlog subsystem from control API at: $subsystem_api_url";
        }
    }
}

sub _resolve_log_level {
    my ($self, $level) = @_;
    if(defined $_MLOG_TEXT_TO_LEVEL->{$level}) {
        $level = $_MLOG_TEXT_TO_LEVEL->{$level};
    } elsif (!(defined $_MLOG_LEVEL_TO_TEXT->{$level})) {
        die "Illegal log level";
    }
    return $level;
}

sub set_log_level {
    my ($self, $level) = @_;
    $self->{_user_log_level} = $self->_resolve_log_level($level);
    $self->{_callback}();
#    if(exists $MLOG_TEXT_TO_LEVEL{$level}) {
#        $level = $MLOG_TEXT_TO_LEVEL{$level};
#    } elsif($level !~ /^\d+$/ || $level < 0 || $level > (@MLOG_LEVELS - 1)) {
#        print STDERR "ERROR: Format for calling set_log_level is set_log_level(integer level) where level can range from 0 to ".(@MLOG_LEVELS - 1)." or be one of '".join("', '",keys %MLOG_TEXT_TO_LEVEL)."'\n";
#        return 1;
#    }
#    $USER_LOG_LEVEL = $level;
}

sub get_log_file {
    my ($self) = @_;
    if ($self->{_user_log_file}) {
        return $self->{_user_log_file};
    }
    if ($self->{_config_log_file}) {
        return $self->{_config_log_file};
    }
    return undef;
}

sub set_log_file {
    my ($self, $filename) = @_;
    $self->{_user_log_file} = $filename;
    $self->{_callback}();
#    $USER_LOG_FILE = $filename;
}

sub set_log_msg_check_count {
    my ($self, $count) = @_;
    if($count !~ /^\d+$/ || $count < 0) {
        die "Format for calling set_log_msg_check_count is set_log_msg_check_count(integer count)\n";
    }
    $self->{_recheck_api_msg} = $count;
#    $MSG_CHECK_COUNT = $count;
}

sub set_log_msg_check_interval {
    my ($self, $interval) = @_;
    if($interval !~ /^\d+$/ || $interval < 0) {
        die "Format for calling set_log_msg_check_interval is set_log_msg_check_interval(integer seconds)\n";
    }
    $self->{_recheck_api_time} = $interval;
#    $MSG_CHECK_INTERVAL = $interval;
}

sub clear_user_log_level {
    my ($self) = @_;
    $self->{_user_log_level} = -1;
#    $USER_LOG_LEVEL = -1;
}

sub _get_ident {
    my ($self, $level, $user, $file, $authuser, $module, $method, $call_id) = @_;
    my @infos = ($self->{_subsystem}, $_MLOG_LEVEL_TO_TEXT->{$level},
                    DateTime->now()->epoch(), $user, $file, $$);
    if ($self->{authuser}) {
        push @infos, $authuser;
    }
    if ($self->{module}) {
        push @infos, $module || '-';
    }if ($self->{method}) {
        push @infos, $method || '-';
    }if ($self->{call_id}) {
        push @infos, $call_id || '-';
    }
    return "[" . join("] [", @infos). "]";
}

sub _syslog {
    my ($self, $facility, $level, $user, $file, $authuser, $module, $method,
        $call_id, $message) = @_;
    setlogsock('unix');
    openlog($self->_get_ident($level, $user, $file, $authuser, $module, $method,
                                $call_id), "", $facility);
    syslog($_MLOG_TO_SYSLOG[$level], "$message");
    closelog();
}

sub _log {
    my ($self, $level, $user, $file, $authuser, $module, $method, $call_id,
        $message) = @_;
    my $msg = join(" ", (localtime(time), hostname, $self->_get_ident(
        $level, $user, $file, $authuser, $module, $method, $call_id) .
        ":" . $message)) + "\n";
    open LOG, ">>$self->_get_log_file()" ||
        warn "Could not print log message $msg to $self->_get_log_file()\n";
    print LOG $msg;
    close LOG;
}

sub logit {
    my ($self, $level, $message, $authuser, $module, $method, $call_id) = @_;
    $level = $self->_resolve_log_level($level);
#    if(@_ != 2 ||
#       ($level !~ /^\d+$/ && (! exists $MLOG_TEXT_TO_LEVEL{$level})) ||
#       ($level =~ /^\d+$/ && ($level < 0 || $level > (@MLOG_LEVELS - 1)))) {
#        print STDERR "ERROR: Format for calling logit is logit(integer level, string message) where level can range from 0 to ".(@MLOG_LEVELS - 1)." or be one of '".join("', '",keys %MLOG_TEXT_TO_LEVEL)."'\n";
#        return 1;
#    }
#
#    if($level !~ /^\d+$/) {
#        $level = $MLOG_TEXT_TO_LEVEL{$level};
#    }
#
#    if($MSG_COUNT == 0 && $TIME_AT_LAST_CONFIG_UPDATE eq "") {
#        print STDERR "WARNING: init_mlog() was not called, so I will call it for you.\n";
#        init_mlog();
#    }

    ++$self->{msg_count};
    ++$self->{_msgs_since_config_update};

    my $user = $ENV{'USER'};
    my $file = abs_path($0);
#    my $logopt = "";

    if($self->{_msgs_since_config_update} >= $self->{_recheck_api_msg} ||
        $self->_get_time_since_start() >= $self->{_recheck_api_time}) {
        $self->update_config();
    }

    # If this message is an emergency, send a copy to the emergency facility first.
    if($level == 0) {
        $self->_syslog($EMERG_FACILITY, $level, $user, $file, $authuser,
            $module, $method, $call_id, $message);
#        setlogsock('unix');
#        openlog("[$SUBSYSTEM] [$MLOG_LEVELS[$level]] [$user] [$ident] [$$]", $logopt, $EMERG_FACILITY);
#        syslog($SYSLOG_LEVEL_TEXT[$level], "$message");
#        closelog();
    }

    if($level <= $self->get_log_level()) {
        $self->_syslog($MSG_FACILITY, $level, $user, $file, $authuser,
            $module, $method, $call_id, $message);
#        setlogsock('unix');
#        openlog("[$SUBSYSTEM] [$MLOG_LEVELS[$level]] [$user] [$ident] [$$]", $logopt, $MSG_FACILITY);
#        syslog($SYSLOG_LEVEL_TEXT[$level], "$message");
#        closelog();
        if($self->get_log_file()) {
            $self._log($level, $user, $file, $authuser, $module, $method,
                $call_id, $message);
        }
#        my $log_file = "";
#        if($USER_LOG_FILE ne "") {
#            $log_file = $USER_LOG_FILE;
#        } elsif($CONFIG_LOG_FILE ne "") {
#            $log_file = $CONFIG_LOG_FILE;
#        }
#
#        if($log_file ne "") {
#            open LOG, ">>$log_file" || print STDERR "Could not print log message to $log_file\n";
#            print LOG localtime(time)." ".hostname." [$SUBSYSTEM] [$MLOG_LEVELS[$level]] [$user] [$ident] [$$]: $message\n";
#            close LOG;
#        }
#    } else {
#        return 1;
    }
}

1;
