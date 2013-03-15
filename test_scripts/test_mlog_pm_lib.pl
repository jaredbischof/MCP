#!/usr/bin/env perl

use strict;
use mlog;

init_mlog();

if(logit(5, "mgrast", "my test message", "error code X")) {
  print "log message sent!\n";
} else {
  print "log message not sent.\n";
}

if(set_log_level(5, "mgrast")) {
  print "log level changed!\n";
} else {
  print "log level not changed.\n";
}

if(logit(5, "mgrast", "test_msg", "error code Y")) {
  print "log message sent!\n";
} else {
  print "log message not sent.\n";
}
