#!/usr/bin/perl

# Copyright 2023 Michael Schlenstedt, michael@loxberry.de
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


##########################################################################
# Modules
##########################################################################

# use Config::Simple '-strict';
# use CGI::Carp qw(fatalsToBrowser);
use CGI;
use LoxBerry::System;
#use LoxBerry::Web;
#use LoxBerry::JSON; # Available with LoxBerry 2.0
#require "$lbpbindir/libs/LoxBerry/JSON.pm";
#use LoxBerry::Log;
#use Time::HiRes qw ( sleep );
use warnings;
use strict;
#use Data::Dumper;

# We do not want to use CGI Module here (takes to long to load...)
print "Content-type: text/plain\n\n";
my %query;
foreach (split(/&/,$ENV{'QUERY_STRING'}))
{
  my ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

if (!$query{"cam"}) {
	print "Missing options. Please read docuةentation at https://wiki.loxberry.de/plugins/motioneye_plugin/start\n";
	exit 1;
}
$query{"cam"} = "0" if !$query{"cam"};

print "Executing command: curl \"http://localhost:7999/$query{'cam'}/config/set?emulate_motion=$query{'motion'}\n\n";
system ("curl \"http://localhost:7999/$query{'cam'}/config/set?emulate_motion=$query{'motion'}\"");
exit;
