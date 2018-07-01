#!/bin/bash

#
# Tuptime installation linux script
# v.1.8.0
#
# Usage:
#	bash tuptime-install.sh		Normal installation
#	bash tuptime-install.sh -d 	Installation using dev branch
#

# Destination dir for executable file
D_BIN='/usr/bin'
# Swich dev branch
DEV=0


# Test arguments
while test $# -gt 0
do
    case "$1" in
        -d) DEV=1
           ;;
    esac
    shift
done


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
		pymod=`python3 -c "import sys, os, argparse, locale, platform, signal, logging, sqlite3, datetime"`
                if [ $? -ne 0 ]; then
                        echo "ERROR: Please, ensure that these Python modules are available in the local system:"
                        echo "sys, os, optparse, sqlite3, locale, platform, datetime, logging"; exit 1
                fi
        fi
fi


# Set Selinux swich
SELX=`getenforce 2> /dev/null`
if [[ ${SELX} != "" ]] && [[ ${SELX} == 'Enforcing' ]]; then
        echo "Selinux enabled in Enforcing"
	SELX='true'
else
	SELX='false'
fi



# Temporary dir for clone repo into it
F_TMP1=`mktemp -d`

echo ""
echo "++ Tuptime installation script ++"
echo ""

echo "+ Cloning repository"
if [ ${DEV} -eq 1 ]; then
        echo "...using dev branch"
	git clone -b dev https://github.com/rfrail3/tuptime.git ${F_TMP1}
else
	git clone https://github.com/rfrail3/tuptime.git ${F_TMP1}
fi

echo "+ Copying files"
install -m 755 ${F_TMP1}/src/tuptime ${D_BIN}/tuptime
if [ ${SELX} = true ]; then restorecon -vF ${D_BIN}/tuptime; fi

echo "+ Creating tuptime user"
useradd --system --no-create-home --home-dir '/var/lib/tuptime' \
        --shell '/bin/false' --comment 'Tuptime execution user' tuptime

echo "+ Creating tuptime db"
tuptime -x

echo "+ Setting tuptime db ownership"
chown -R tuptime:tuptime /var/lib/tuptime
chmod 755 /var/lib/tuptime

echo "+ Executing tuptime with tuptime user for testing"
su -s /bin/sh tuptime -c "tuptime -x"

systemctl --version &> /dev/null
if [ $? -eq 0 ]; then
	echo "+ Copying systemd file"
	cp -a ${F_TMP1}/src/systemd/tuptime.service  /lib/systemd/system/
	if [ ${SELX} = true ]; then restorecon -vF /lib/systemd/system/tuptime.service; fi
	systemctl daemon-reload
	systemctl enable tuptime.service && systemctl start tuptime.service
elif [ -f /etc/rc.d/init.d/functions ]; then
	echo "+ Copying init redhat file"
	install -m 755 ${F_TMP1}/src/init.d/redhat/tuptime /etc/init.d/tuptime
	if [ ${SELX} = true ]; then restorecon -vF /etc/init.d/tuptime; fi
	chkconfig --add tuptime
	chkconfig tuptime on
elif [ -f /lib/lsb/init-functions ]; then
	echo "+ Copying init debian file"
	install -m 755 ${F_TMP1}/src/init.d/debian/tuptime /etc/init.d/tuptime
	if [ ${SELX} = true ]; then restorecon -vF /etc/init.d/tuptime; fi
	update-rc.d tuptime defaults
else
	echo "#####################################"
	echo "ERROR - Any init file for your system"
	echo "#####################################"
fi

if [ -d /etc/cron.d/ ]; then
	echo "+ Copying cron file"
	cp -a ${F_TMP1}/src/cron.d/tuptime /etc/cron.d/tuptime
	if [ ${SELX} = true ]; then restorecon -vF /etc/cron.d/tuptime; fi
else
	echo "+ Copying tuptime-cron.timer and .service"
	cp -a ${F_TMP1}/src/systemd/tuptime-cron.*  /lib/systemd/system/
	if [ ${SELX} = true ]; then restorecon -vF /lib/systemd/system/tuptime-cron.*; fi
	systemctl enable tuptime-cron.timer && systemctl start tuptime-cron.timer
fi

echo ""
echo "+ Enjoy!"
echo ""

tuptime
