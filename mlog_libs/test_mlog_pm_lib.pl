#!/usr/bin/env perl

use strict;
use mlog;

################################################################################

init_mlog("pipeline");
print "log_level = ".get_log_level()."\n";

logit(2, "my test message at log level 2 with no constraints");
logit(3, "my test message at log level 3 with no constraints");
logit(4, "my test message at log level 4 with no constraints");

################################################################################

my %log_constraints = ('job' => '3', 'stage' => '350');
init_mlog("pipeline", \%log_constraints);
print "log_level = ".get_log_level()."\n";

logit(2, "my test message at log level 2 with constraints job=3 and stage=350");
logit(3, "my test message at log level 3 with constraints job=3 and stage=350");
logit(4, "my test message at log level 4 with constraints job=3 and stage=350");

################################################################################

set_log_level(5);
print "log_level = ".get_log_level()."\n";

logit(2, "my test message at log level 2 with constraints job=3 and stage=350");
logit(3, "my test message at log level 3 with constraints job=3 and stage=350");
logit(4, "my test message at log level 4 with constraints job=3 and stage=350");

################################################################################

#logit('emergency', "this program is finished");
