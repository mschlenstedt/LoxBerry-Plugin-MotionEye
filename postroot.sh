#!/bin/bash
 
# Shell script which is executed by bash *AFTER* complete installation is done
# (*AFTER* postinstall and *AFTER* postupdate). Use with caution and remember,
# that all systems may be different!
#
# Exit code must be 0 if executed successfull.
# Exit code 1 gives a warning but continues installation.
# Exit code 2 cancels installation.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Will be executed as user "root".
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# You can use all vars from /etc/environment in this script.
#
# We add 5 additional arguments when executing this script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"
 
# To use important variables from command line use the following code:
COMMAND=$0    # Zero argument is shell command
PTEMPDIR=$1   # First argument is temp folder during install
PSHNAME=$2    # Second argument is Plugin-Name for scipts etc.
PDIR=$3       # Third argument is Plugin installation folder
PVERSION=$4   # Forth argument is Plugin version
#LBHOMEDIR=$5 # Comes from /etc/environment now. Fifth argument is
              # Base folder of LoxBerry
PTEMPPATH=$6  # Sixth argument is full temp path during install (see also $1)
 
# Combine them with /etc/environment
PHTMLAUTH=$LBPHTMLAUTH/$PDIR
PHTML=$LBPHTML/$PDIR
PTEMPL=$LBPTEMPL/$PDIR
PDATA=$LBPDATA/$PDIR
PLOG=$LBPLOG/$PDIR # Note! This is stored on a Ramdisk now!
PCONFIG=$LBPCONFIG/$PDIR
PSBIN=$LBPSBIN/$PDIR
PBIN=$LBPBIN/$PDIR

echo "<INFO> Install newest pip2 version..."
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output /tmp/get-pip.py
python2 /tmp/get-pip.py
rm /tmp/get-pip.py

echo "<INFO> Installing setuptools via pip..."
yes | python2 -m pip setuptools

INSTALLED_ST=$(python2 -m pip list --format=columns | grep "setuptools" | grep -v grep | wc -l)
if [ ${INSTALLED_ST} -ne "0" ]; then
	echo "<OK> Setuptools installed successfully."
else
	echo "<FAIL> Setuptools could not be installed."
	exit 2;
fi 
 
echo "<INFO> Installing motioneye via pip..."
yes | python2 -m pip install motioneye

INSTALLED_ME=$(python2 -m pip list --format=columns | grep "motioneye" | grep -v grep | wc -l)
if [ ${INSTALLED_ME} -ne "0" ]; then
	echo "<OK> MotionEye installed successfully."
else
	echo "<FAIL> MotionEye could not be installed."
	exit 2;
fi 

echo "<INFO> Creating /etc/motioneye..."
ln -s $PCONFIG /etc/motioneye

echo "<INFO> Deleting Motion Logrotate..."
rm /etc/logrotate.d/motion

echo "<INFO> Adding user loxberry to video group..."
usermod -a -G video loxberry

echo "<INFO> Installing MotionEye Servicefile..."
cp $PTEMPL/motioneye.systemd-unit-local /etc/systemd/system/motioneye.service
# If Shebang is still /usr/bin/python, change it to /usr/bin/python2
sed -i 's/^#!\(.*\)python$/#!\1python2/' /usr/local/bin/meyectl
systemctl daemon-reload
systemctl enable motioneye
systemctl start motioneye

# Motion is handled by MotionEye - so disable it here
systemctl stop motion
systemctl disable motion

# Exit with Status 0
exit 0
