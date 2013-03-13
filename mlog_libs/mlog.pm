package mlog;

@ISA = qw(Exporter);
@EXPORT = qw(init_mlog set_log_level set_log_msg_check_count set_log_msg_check_interval logit use_all_api_log_levels use_api_log_level);

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
my $MSG_CHECK_COUNT = 100;
my $MSG_CHECK_INTERVAL = 300; # 300s = 5min
my @LOG_LEVEL_TEXT = ( 'emerg', 'alert', 'crit', 'err',
                         'warning', 'notice', 'info', 'debug' );

my %api_defined_log_levels = ();
my %user_defined_log_levels = ();
my $msg_count = 0;
my $last_update_time = "";
my $last_update_msg_count = 0;

1;

=pod

=head1 NAME

mlog

=head1 DESCRIPTION

A library for sending MG-RAST logging to syslog.

=head1 METHODS

init_mlog(): Initializes mlog. It's good to call this at the beginning of your program.

logit(level, component, message, error_code): sends mgrast log message to syslog.

=over 10

=item * level: (0-6) The logging level for this message is compared to the logging level that has been set in mlog.  If it is <= the set logging level, the message will be sent to syslog, otherwise it will be ignored.  Logging level is set to 6 if MG-RAST control API cannot be reached.

=item * component: (string) This is the utility within MG-RAST that is logging the message.  This is a free text field.

=item * message: (string) This is the log message.

=item * error_code: (string) The error code for this log message.

=back

set_log_level(integer level, string component) : Sets the logging level of the given component. Only use this if you wish to override the log levels that are defined by the control API.

=over 10

=item * level : priority

=item * 0 : emergencies - vital component is down

=item * 1 : alerts - non-vital component is down

=item * 2 : errors - error that prevents proper operation

=item * 3 : warning - error, but does not prevent operation

=item * 4 : debug - lowest level of debug

=item * 5 : debug2 - second level of debug

=item * 6 : debug3 - highest level of debug

=back

set_log_msg_check_count(integer count): used to set the number the messages that mlog will log before querying the control API for the log level of all components (default is 100 messages).

set_log_msg_check_interval(integer seconds): used to set the interval, in seconds, that will be allowed to pass before  mlog will  query the control API for the log level of the given component (default is 300 seconds).

use_all_api_log_levels() : Removes all user-defined log levels and tells mlog to use the control API defined log levels.

use_api_log_level(string component) : Removes the user-defined log level for this component and tells mlog to use the control API defined log levels.

=cut

sub init_mlog {
    $last_update_msg_count = 0;
    $last_update_time = DateTime->now( time_zone => 'local' )->set_time_zone('floating');

    # Retrieving the control API defined log levels...
    my $api_mlog_url = "";
    open IN, "$MLOG_CONF_FILE" || print STDERR "Cannot open $MLOG_CONF_FILE for reading mlog configuration.\n";
    while(my $line=<IN>) {
        chomp $line;
        if($line =~ /^url\s+.*$/) {
            my @array = split(/\s+/, $line);
            $api_mlog_url = $array[1];
        }
    }
    close IN;
    unless($api_mlog_url eq "") {
        my $json = get($api_mlog_url);
        if(defined $json) {
            my $decoded_json = decode_json($json);
            foreach my $component (@{$decoded_json->{'components'}}) {
                $api_defined_log_levels{$component->{'name'}} = $component->{'log_level'};
            }
        } else {
            print STDERR "Could not retrieve mlog resource from control API at: $api_mlog_url\n";
        }
    }
    return 1;
}

sub _get_log_level {
    my ($component) = @_;
    if(exists $user_defined_log_levels{$component}) {
        return $user_defined_log_levels{$component};
    } elsif(exists $api_defined_log_levels{$component}) {
        return $api_defined_log_levels{$component};
    } else {
        return $DEFAULT_LOG_LEVEL;
    }
}

sub _get_time_since_start {
    my $now = DateTime->now( time_zone => 'local' )->set_time_zone('floating');
    my $seconds_duration = $now->subtract_datetime_absolute($last_update_time);
    return $seconds_duration->seconds;
}

sub set_log_level {
    my ($level, $component) = @_;
    if($level !~ /^\d+$/ || $component eq "") {
        print STDERR "ERROR: Format for calling set_log_level is set_log_level(integer level, string component)\n";
        return 0;
    }
    $user_defined_log_levels{$component} = $level;
    return 1;
}

sub set_log_msg_check_count {
    my ($count) = @_;
    if($count !~ /^\d+$/) {
        print STDERR "ERROR: Format for calling set_log_msg_check_count is set_log_msg_check_count(integer count)\n";
        return 0;
    }
    $MSG_CHECK_COUNT = $count;
    return 1;
}

sub set_log_msg_check_interval {
    my ($interval) = @_;
    if($interval !~ /^\d+$/) {
        print STDERR "ERROR: Format for calling set_log_msg_check_interval is set_log_msg_check_interval(integer seconds)\n";
        return 0;
    }
    $MSG_CHECK_INTERVAL = $interval;
    return 1;
}

sub use_all_api_log_levels {
    %user_defined_log_levels = ();
}

sub use_api_log_level {
    my ($component) = @_;
    if($component eq "") {
        print STDERR "ERROR: Format for calling use_api_log_level is use_api_log_level(string component)\n";
        return 0;
    }
    delete $user_defined_log_levels{$component};
}

sub logit {
    my ($level, $component, $message, $error_code) = @_;
    if($level !~ /^\d+$/ || $component eq "" || @_ != 4) {
        print STDERR "ERROR: Format for calling logit is logit(integer level, string component, string message, string error_code)\n";
        return 0;
    }

    unless($level =~ /^\d+$/ && $level >= 0 && $level <= 6) {
      print STDERR "ERROR: mlog level '$level' is invalid, you must enter an integer between 0 and 6, inclusive.\n";
      return 0;
    }

    ++$msg_count;
    ++$last_update_msg_count;

    if($msg_count == 0 && $last_update_time eq "") {
        print STDERR "WARNING: mlog_init() was not called, so I will call it for you.\n";
        mlog_init();
    }

    # May want to include these in 1st openlog argument
    my $user = $ENV{'USER'};
    my $ident = abs_path($0);
    my $logopt = "";
    my $msg_facility = 'local1';
    my $emerg_facility = 'local0';

    if($last_update_msg_count >= $MSG_CHECK_COUNT || _get_time_since_start() >= $MSG_CHECK_INTERVAL) {
        mlog_init();
    }

    # If this message is an emergency, send a copy to the emergency facility
    if($level == 0) {
        setlogsock('unix');
        openlog("$component:$user:$$:$ident:$error_code", $logopt, $emerg_facility);
        syslog($LOG_LEVEL_TEXT[$level], "$message");
        closelog();
    }

    if($level <= _get_log_level($component)) {
        setlogsock('unix');
        openlog("$component:$user:$$:$ident:$error_code", $logopt, $msg_facility);
        syslog($LOG_LEVEL_TEXT[$level], "$message");
        closelog();
    } else {
        return 0;
    }

    return 1;
}

1;
