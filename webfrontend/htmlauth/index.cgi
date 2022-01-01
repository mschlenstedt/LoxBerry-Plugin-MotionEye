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
#use Data::Dumper;

##########################################################################
# Variables
##########################################################################

# Read Form
my $cgi = CGI->new;
my $q = $cgi->Vars;

my $version = LoxBerry::System::pluginversion();

# Language Phrases
my %L;

require LoxBerry::Web;

# Template
my $templatefile = "$lbptemplatedir/settings.html";
my $template = LoxBerry::System::read_file($templatefile);

# Add JS Scripts to template
$templatefile = "$lbptemplatedir/javascript.html";
$template .= LoxBerry::System::read_file($templatefile);

my $templateout = HTML::Template->new_scalar_ref(
	\$template,
	global_vars => 1,
	loop_context_vars => 1,
	die_on_bad_params => 0,
);

# Language File
%L = LoxBerry::System::readlanguage($templateout, "language.ini");

# Navbar
my $host = "$ENV{HTTP_HOST}";
my $port = qx ( cat $lbpconfigdir/motioneye.conf | grep -e "^port.*" | cut -d " " -f2 );
chomp $port;

our %navbar;
$navbar{1}{Name} = "$L{'COMMON.LABEL_ME_WEBUI'}";
$navbar{1}{URL} = "http://$host:$port";
$navbar{1}{target} = '_blank';

$navbar{2}{Name} = "$L{'COMMON.LABEL_MULTIVIEW'}";
$navbar{2}{URL} = "/plugins/$lbpplugindir/index.cgi";
$navbar{2}{target} = '_blank';

$navbar{3}{Name} = "$L{'COMMON.LABEL_LOGFILES'}";
$navbar{3}{URL} = "/admin/system/tools/logfile.cgi?logfile=plugins/$lbpplugindir/motion.log&header=html&format=template";
$navbar{3}{target} = '_blank';

# Template Vars
$templateout->param("MEWEBUILINK", "http://$host:$port");

# Print out Template
LoxBerry::Web::lbheader($L{'COMMON.LABEL_PLUGINTITLE'} . " V$version", "https://www.loxwiki.eu/x/3gmcAw", "");
print $templateout->output();
LoxBerry::Web::lbfooter();
	
exit;

