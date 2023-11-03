#!/usr/bin/perl

# Copyright 2019 Michael Schlenstedt, michael@loxberry.de
#                Christian Fenzl, christian@loxberry.de
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
use Data::Dumper;

my $host = "$ENV{HTTP_HOST}";
$host = LoxBerry::System::get_localip() if (!$host);

# Read configured cameras
opendir(my $fh,"$lbpconfigdir");
my @files = readdir($fh);
close $fh;

my @streams;
foreach my $file (@files) {
	if ( $file =~ /^camera-(\d+)\.conf/ ) {
		#print STDERR "Found file $file\n";
		my $cam = $1;
		my $content = LoxBerry::System::read_file("$lbpconfigdir/$file");
		if ($content) {
			my @lines = split("\n", $content);
			my %stream;
			foreach my $line (@lines) {
				$stream{"No"} = "$cam";
				if ( $line =~ /^stream_port (\d+)$/ ) { # Network cam
					$stream{"Url"} = "http://$host:$1";
				} 
				elsif ( $line =~ /^# \@url (.*)$/ ) { # MJPEG only Cams
					$stream{"Url"} = "$1";
				}
				elsif ( $line =~ /^# \@url (.*)$/ ) { # MJPEG only Cams
					$stream{"Url"} = "$1";
				}
				elsif ( $line =~ /^stream_localhost off$/ ) { # Enabled streaming
					$stream{"Enabled"} = 1;
				}
			}
			if ( $stream{"Url"} && $stream{"Enabled"} ) {
				push (@streams, \%stream);
			}
		}
	}
}

#print Dumper @streams;

# We do not want to use CGI Module here (takes to long to load...)
my %query;
print "Content-type: text/html\n\n";
foreach (split(/&/,$ENV{'QUERY_STRING'}))
{
  my ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

print <<EOF;
<html>
<head>
<title>Camera MultiView</title>
<META content="text/html"; charset="UTF-8"; http-equiv=Content-Type>
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1">
</head>
<body>
<center>
EOF

if ( $query{"cam"} ) {

	print "<a href=\"./index.cgi\"><img src=\"";
	foreach my $stream (@streams) {
		if ( %$stream{"No"} eq $query{"cam"} ) {
			print %$stream{"Url"} . "\"></a>\n";
			last;
		}
	}

} elsif (scalar(@streams) < 1) {

	print "<img src=\"./images/motioneye_128.png\"><br><br>";
	print "There seems to be no cameras configured yet. Add cameras in the MotionEye WebUI first and activate Video Streaming.";

} else {

	foreach my $stream (@streams) {
		print "<a href=\"./index.cgi?cam=" . %$stream{"No"} . "\"><img src=\"" . %$stream{"Url"} . "\" width=\"320\"></a>\n";
	}
}

print <<EOF;
</center>
</body>
</html>
EOF

exit;
