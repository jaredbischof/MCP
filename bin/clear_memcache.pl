#!/usr/bin/env perl

use strict;
use Cache::Memcached;
use Data::Dumper;

my $memhost = "kursk-2.mcs.anl.gov:11211";
my $mem_cache = new Cache::Memcached {"servers" => [$memhost], "debug" => 1, "compress_threshold" => 10_000};
my $mem_cache->flush_all;
