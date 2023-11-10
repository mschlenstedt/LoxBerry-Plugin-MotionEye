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
use Image::Magick;

# We do not want to use CGI Module here (takes to long to load...)
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
	print "Content-type: text/plain\n\n";
	print "Missing options. Please read docuةentation at https://wiki.loxberry.de/plugins/motioneye_plugin/start\n";
	exit 1;
}

my $configfile = "$lbpconfigdir" . "/camera-" . $query{'cam'} . ".conf";
if (!-e $configfile) {
	print "Content-type: text/plain\n\n";
	print "Config file for Camera ID $query{'cam'} does not exist.";
	exit 1;
}

# Set Motion status
if ($query{"motion"} ne "") {

	print "Content-type: text/plain\n\n";

	$query{"motion"} = "0" if !$query{"motion"};

	print "Executing command: curl \"http://localhost:7999/$query{'cam'}/config/set?emulate_motion=$query{'motion'}\n\n";
	system ("curl \"http://localhost:7999/$query{'cam'}/config/set?emulate_motion=$query{'motion'}\"");
	print "\n\n";

}

if ($query{"mail"} eq "1") {

	print "Content-type: text/plain\n\n";

	if (!$query{"to"}) {
		print "Missing options. Please read docuةentation at https://wiki.loxberry.de/plugins/motioneye_plugin/start\n";
		exit 1;
	}

	my @recipients = split(',', $query{"to"});
	my $recipients;
	for (@recipients){
		$recipients = $recipients . " $_";
	}

	my $targetdir = qx (cat $configfile | grep target_dir | cut -d' ' -f2);
	chomp $targetdir;

	if (!-d $targetdir) {
		print "Target dir for Camera ID $query{'cam'} does not exist.";
		exit 1;
	}

	print "Executing command: curl \"http://localhost:7999/$query{'cam'}/action/snapshot\n\n";
	system ("curl \"http://localhost:7999/$query{'cam'}/action/snapshot\"");
	print "\n\n";
	sleep 0.5;

	if (!-e "$targetdir/lastsnap.jpg") {
		print "Last Snapshot in $targetdir does not exist.";
		exit 1;
	}

	my $image = Image::Magick->new();
	my $x = $image->Read(filename =>"$targetdir/lastsnap.jpg");
	if ($x) {
		print "Error: $x";
		exit 1;
	}

	if ($query{"resize"}) {
		$image->Resize(geometry=>$query{'resize'});
		if ($x) {
			print "Error: $x";
			exit 1;
		}
	}

	$image->Write(filename=>"/tmp/lastsnap_$query{'cam'}.jpg");
	if ($x) {
		print "Error: $x";
		exit 1;
	}

	$query{"text"} = "This is Motioneye. Please find attached the last Snapshot of Camera ID " . $query{'cam'} if !$query{"text"};
	$query{"subject"} = "Snapshot from MotionEye from Camera ID " . $query{'cam'} if !$query{"subject"};

	print "Executing command: printf \"$query{'text'}\" | s-nail -a \"/tmp/lastsnap_$query{'cam'}.jpg\" -s \"$query{'subject'}\" $recipients\n\n";
	system ("printf \"$query{'text'}\" | s-nail -a \"/tmp/lastsnap_$query{'cam'}.jpg\" -s \"$query{'subject'}\" $recipients");
	print "\n\n";

	unlink ("$targetdir/lastsnap.jpg");

}

if ($query{"show"} eq "1") {

	my $targetdir = qx (cat $configfile | grep target_dir | cut -d' ' -f2);
	chomp $targetdir;

	if (!-d $targetdir) {
		print "Content-type: text/plain\n\n";
		print "Target dir for Camera ID $query{'cam'} does not exist.";
		exit 1;
	}

	system ("curl \"http://localhost:7999/$query{'cam'}/action/snapshot\" > /dev/null 2>&1");
	sleep 0.5;

	if (!-e "$targetdir/lastsnap.jpg") {
		print "Content-type: text/plain\n\n";
		print "Last Snapshot in $targetdir does not exist.";
		exit 1;
	}

	my $image = Image::Magick->new();
	my $x = $image->Read(filename =>"$targetdir/lastsnap.jpg");
	if ($x) {
		print "Content-type: text/plain\n\n";
		print "Error: $x";
		exit 1;
	}

	if ($query{"resize"}) {
		$image->Resize(geometry=>$query{'resize'});
		if ($x) {
			print "Content-type: text/plain\n\n";
			print "Error: $x";
			exit 1;
		}
	}

	print "Content-type: image/jpeg\n\n";
	binmode STDOUT;
	$image->Write('jpg:-');

}

exit;
