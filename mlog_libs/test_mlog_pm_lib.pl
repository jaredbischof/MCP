#!/usr/bin/env perl

use strict;
use mlog;

################################################################################

my $m = mlog->new("pipeline");
print "log_level = ".$m->get_log_level()."\n";

$m->logit(3, "my test message at log level 3 with no constraints");
$m->logit(4, "my test message at log level 4 with no constraints");
$m->logit(5, "my test message at log level 5 with no constraints");

################################################################################

my %log_constraints = ('job' => '3', 'stage' => '350');
$m = mlog->new("pipeline", \%log_constraints);
print "log_level = ".$m->get_log_level()."\n";

$m->logit(3, "my test message at log level 3 with constraints job=3 and stage=350");
$m->logit(4, "my test message at log level 4 with constraints job=3 and stage=350");
$m->logit(5, "my test message at log level 5 with constraints job=3 and stage=350");

################################################################################

$m->set_log_file("foo");
$m->set_log_level(5);
print "log_level = ".$m->get_log_level()."\n";

$m->logit(3, "my test message at log level 3 with constraints job=3 and stage=350");
$m->logit(4, "my test message at log level 4 with constraints job=3 and stage=350");
$m->logit(5, "my test message at log level 5 with constraints job=3 and stage=350");

################################################################################

#logit('emergency', "this program is finished");
