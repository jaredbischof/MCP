package mlog;

@ISA = qw(Exporter);
@EXPORT = qw(init_mlog get_log_level update_api_log_level set_log_level set_log_msg_check_count set_log_msg_check_interval use_api_log_level logit);

use strict;
use warnings;
use LWP::Simple;
use JSON qw( decode_json );
use DateTime;
use Cwd 'abs_path';
use Data::Dumper;

use Sys::Syslog qw( :DEFAULT setlogsock);

require Exporter;

my $MLOG_CONF_FILE = "/etc/mlog/mlog.conf";
my $DEFAULT_LOG_LEVEL = 6;
my $LOG_LEVEL_MIN = 0;
my $LOG_LEVEL_MAX = 6;
my $MSG_CHECK_COUNT = 100;
my $MSG_CHECK_INTERVAL = 300; # 300s = 5min
my $MSG_FACILITY = 'local1';
my $EMERG_FACILITY = 'local0';
my @SYSLOG_LEVEL_TEXT  = ( 'emerg', 'alert', 'crit', 'err',
                           'warning', 'notice', 'info', 'debug' );
my %MLOG_TEXT_TO_LEVEL = ( 'EMERGENCY' => 0,
                           'ALERT' => 1, 
                           'ERROR' => 2,
                           'WARNING' => 3,
                           'DEBUG' => 4,
                           'DEBUG2' => 5,
                           'DEBUG3' => 6 );
my @MLOG_LEVELS = ( 'EMERGENCY', 'ALERT', 'ERROR',
                    'WARNING', 'DEBUG', 'DEBUG2', 'DEBUG3' );

my $subsystem = "";
my $api_log_level = -1;
my $user_log_level = -1;
my $log_constraints;
my $msg_count = 0;
my $time_since_api_update = "";
my $msgs_since_api_update = 0;

1;

=pod

=head1 NAME

mlog

=head1 DESCRIPTION

A library for sending MG-RAST logging to syslog.

=head1 METHODS

init_mlog(string subsystem, hashref constraints): Initializes mlog. You should call this at the beginning of your program. Constraints are optional.

logit(int level, string message): sends mgrast log message to syslog.

=over 10

=item * level: (0-6) The logging level for this message is compared to the logging level that has been set in mlog.  If it is <= the set logging level, the message will be sent to syslog, otherwise it will be ignored.  Logging level is set to 6 if MG-RAST control API cannot be reached and the user does not set the log level. Log level can also be entered as string (e.g. 'DEBUG')

=item * message: This is the log message.

=back

get_log_level(): Returns the current log level as an integer.

set_log_level(integer level) : Sets the log level. Only use this if you wish to override the log levels that are defined by the control API. Can also be entered as string (e.g. 'DEBUG')

=over 10

=item * level : priority

=item * 0 : EMERGENCY - vital component is down

=item * 1 : ALERT - non-vital component is down

=item * 2 : ERROR - error that prevents proper operation

=item * 3 : WARNING - error, but does not prevent operation

=item * 4 : DEBUG - lowest level of debug

=item * 5 : DEBUG2 - second level of debug

=item * 6 : DEBUG3 - highest level of debug

=back

set_log_msg_check_count(integer count): used to set the number the messages that mlog will log before querying the control API for the log level (default is 100 messages).

set_log_msg_check_interval(integer seconds): used to set the interval, in seconds, that will be allowed to pass before mlog will query the control API for the log level (default is 300 seconds).

update_api_log_level() : Checks the control API for the currently set log level.

use_api_log_level() : Removes the user-defined log level and tells mlog to use the control API-defined log level.

=cut

sub init_mlog {
    my ($sub, $lc) = @_;
    unless(defined $sub) {
        print STDERR "ERROR: You must define a subsystem when calling init_log()\n";
        return 1;
    }
    $subsystem = $sub;
    if(defined $lc) {
        $log_constraints = $lc;
    }
    $user_log_level = -1;
    $msg_count = 0;
    update_api_log_level();
}

sub _get_time_since_start {
    my $now = DateTime->now( time_zone => 'local' )->set_time_zone('floating');
    my $seconds_duration = $now->subtract_datetime_absolute($time_since_api_update);
    return $seconds_duration->seconds;
}

sub get_log_level {
    if($user_log_level != -1) {
        return $user_log_level;
    } elsif($api_log_level != -1) {
        return $api_log_level;
    } else {
        return $DEFAULT_LOG_LEVEL;
    }
}

sub update_api_log_level {
    $api_log_level = -1;
    $msgs_since_api_update = 0;
    $time_since_api_update = DateTime->now( time_zone => 'local' )->set_time_zone('floating');

    # Retrieving the control API defined log level
    my $api_url = "";
    open IN, "$MLOG_CONF_FILE" || print STDERR "Cannot open $MLOG_CONF_FILE for reading mlog configuration.\n";
    while(my $line=<IN>) {
        chomp $line;
        if($line =~ /^url\s+.*$/) {
            my @array = split(/\s+/, $line);
            $api_url = $array[1];
        }
    }
    close IN;

    unless($api_url eq "") {
        my $subsystem_api_url = $api_url."/$subsystem";
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
                    if(! exists $log_constraints->{$constraint}) {
                        $matches = 0;
                    } elsif($log_constraints->{$constraint} ne $constraints->{$constraint}) {
                        $matches = 0;
                    }
                }
                if($matches == 1) {
                    $max_matching_level = $level;
                }
            }
            $api_log_level = $max_matching_level;
        } else {
            print STDERR "Could not retrieve mlog subsystem from control API at: $subsystem_api_url\n";
        }
    }
}

sub set_log_level {
    my ($level) = @_;
    if(exists $MLOG_TEXT_TO_LEVEL{$level}) {
        $level = $MLOG_TEXT_TO_LEVEL{$level};
    } elsif($level !~ /^\d+$/ || $level < $LOG_LEVEL_MIN || $level > $LOG_LEVEL_MAX) {
        print STDERR "ERROR: Format for calling set_log_level is set_log_level(integer level) where level can range from $LOG_LEVEL_MIN to $LOG_LEVEL_MAX or be one of '".join("', '",keys %MLOG_TEXT_TO_LEVEL)."'\n";
        return 1;
    }
    $user_log_level = $level;
}

sub set_log_msg_check_count {
    my ($count) = @_;
    if($count !~ /^\d+$/) {
        print STDERR "ERROR: Format for calling set_log_msg_check_count is set_log_msg_check_count(integer count)\n";
        return 1;
    }
    $MSG_CHECK_COUNT = $count;
}

sub set_log_msg_check_interval {
    my ($interval) = @_;
    if($interval !~ /^\d+$/) {
        print STDERR "ERROR: Format for calling set_log_msg_check_interval is set_log_msg_check_interval(integer seconds)\n";
        return 1;
    }
    $MSG_CHECK_INTERVAL = $interval;
}

sub use_api_log_level {
    $user_log_level = -1;
}

sub logit {
    my ($level, $message) = @_;
    if(@_ != 2 ||
       ($level !~ /^\d+$/ && (! exists $MLOG_TEXT_TO_LEVEL{$level})) ||
       ($level =~ /^\d+$/ && ($level < $LOG_LEVEL_MIN || $level > $LOG_LEVEL_MAX))) {
        print STDERR "ERROR: Format for calling logit is logit(integer level, string message) where level can range from $LOG_LEVEL_MIN to $LOG_LEVEL_MAX or be one of '".join("', '",keys %MLOG_TEXT_TO_LEVEL)."'\n";
        return 1;
    }

    if($level !~ /^\d+$/) {
        $level = $MLOG_TEXT_TO_LEVEL{$level};
    }

    if($msg_count == 0 && $time_since_api_update eq "") {
        print STDERR "WARNING: init_mlog() was not called, so I will call it for you.\n";
        init_mlog();
    }

    ++$msg_count;
    ++$msgs_since_api_update;

    my $user = $ENV{'USER'};
    my $ident = abs_path($0);
    my $logopt = "";

    if($msgs_since_api_update >= $MSG_CHECK_COUNT || _get_time_since_start() >= $MSG_CHECK_INTERVAL) {
        update_api_log_level();
    }

    # If this message is an emergency, send a copy to the emergency facility first.
    if($level == 0) {
        setlogsock('unix');
        openlog("[$subsystem] [$MLOG_LEVELS[$level]] [$user] [$ident] [$$]", $logopt, $EMERG_FACILITY);
        syslog($SYSLOG_LEVEL_TEXT[$level], "$message");
        closelog();
    }

    if($level <= get_log_level($subsystem)) {
        setlogsock('unix');
        openlog("[$subsystem] [$MLOG_LEVELS[$level]] [$user] [$ident] [$$]", $logopt, $MSG_FACILITY);
        syslog($SYSLOG_LEVEL_TEXT[$level], "$message");
        closelog();
    } else {
        return 1;
    }
}

1;
