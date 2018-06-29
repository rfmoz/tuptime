#!/bin/bash

#
# Tuptime installation linux script
# v.1.7.1
#

# Destination dir for executable file
D_BIN='/usr/bin'


# Test if is a linux system
if [ "$(expr substr $(uname -s) 1 5)" != "Linux" ]; then
	echo "Sorry, only for Linux systems"
	exit 1
fi


# Test if git is installed
git --version &> /dev/null
if [ $? -ne 0 ]; then
	echo "ERROR: \"git\" command not available"
	echo "Please, install it"; exit 1
fi


# Test if python is installed
pyver=`python3 --version 2>&1 /dev/null`
if [ $? -ne 0 ]; then
        echo "ERROR: Python not available"
        echo "Please, install version 3 or greater"; exit 1
else
	# Test if version 3 or avobe of python is installed
        pynum=`echo ${pyver} | tr -d '.''' | grep -Eo  '[0-9]*' | head -1 | cut -c 1-2`
        if [ $pynum -lt 30 ] ; then
                echo "ERROR: Its needed Python version 3, not ${pyver}"
                echo "Please, upgrade it."; exit 1
        else
		# Test if all modules needed are available
		pymod=`python -c "sys, os, argparse, locale, platform, signal, logging, sqlite3, datetime"`
                if [ $? -ne 0 ]; then
                        echo "ERROR: Please, ensure that these Python modules are available in the local system:"
                        echo "sys, os, optparse, sqlite3, locale, platform, datetime, logging"
                fi
        fi
fi


# Temporary dir for clone repo into it
F_TMP1=`mktemp -d`

echo "Tuptime installation script"
echo ""

echo "Clonning repository..."
git clone https://github.com/rfrail3/tuptime.git ${F_TMP1}

#echo "Swich to dev branch"
#cd ${F_TMP1}/
#git checkout -b dev origin/dev

echo "Copying files..."
cp -a ${F_TMP1}/src/tuptime ${D_BIN}/tuptime
chmod 755 ${D_BIN}/tuptime

echo "Creating tuptime user..."
useradd --system --no-create-home --home-dir '/var/lib/tuptime' \
        --shell '/bin/false' --comment 'Tuptime execution user,,,' tuptime

echo "Creating tuptime db"
tuptime -x

echo "Setting tuptime db ownership"
chown -R tuptime:tuptime /var/lib/tuptime
chmod 755 /var/lib/tuptime

echo "Executing tuptime with tuptime user for testing"
su -s /bin/sh tuptime -c "tuptime -x"

systemctl --version &> /dev/null
if [ $? -eq 0 ]; then
	echo "Copying systemd file..."
	cp -a ${F_TMP1}/src/systemd/tuptime.service  /lib/systemd/system/
	systemctl daemon-reload
	systemctl enable tuptime.service
	systemctl start tuptime.service
elif [ -f /etc/rc.d/init.d/functions ]; then
	echo "Copying init redhat file..."
	cp -a ${F_TMP1}/src/init.d/redhat/tuptime /etc/init.d/tuptime
	chmod 755 /etc/init.d/tuptime
	chkconfig --add tuptime
	chkconfig tuptime on
elif [ -f /lib/lsb/init-functions ]; then
	echo "Copying init debian file..."
	cp -a ${F_TMP1}/src/init.d/debian/tuptime /etc/init.d/tuptime
	chmod 755 /etc/init.d/tuptime
	update-rc.d tuptime defaults
else
	echo "#####################################"
	echo "ERROR - Any init file for your system"
	echo "#####################################"
fi

echo "Copying cron file..."
cp -a ${F_TMP1}/src/cron.d/tuptime /etc/cron.d/tuptime

echo "Enjoy!"

tuptime
