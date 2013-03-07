#!/usr/bin/env perl

use strict;
use Cache::Memcached;
use Data::Dumper;

if(@ARGV < 1) {
  print "Usage: $0 <memhost:port>\n";
  exit;
}

my $memhost = $ARGV[0];
my $mem_cache = new Cache::Memcached {"servers" => [$memhost], "debug" => 1, "compress_threshold" => 10_000};
my $mem_cache->flush_all;
