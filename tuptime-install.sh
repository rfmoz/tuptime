#!/bin/bash

#
# Tuptime installation script
# v.1.2
#

git --version &> /dev/null
if [ $? -ne 0 ]; then
	echo "ERROR: \"git\" command not available"
	echo "Please, install it"; exit 1
fi


pyver=`python --version 2>&1 /dev/null`
if [ $? -ne 0 ]; then
        echo "ERROR: Python not available"
        echo "Please, install version 2.7 or greater (3.X recomended)"; exit 1
else
        pynum=`echo ${pyver} | tr -d '.''' | grep -Eo  '[0-9]*' | cut -c 1-2`
        if [ $pynum -lt 27 ] ; then
                echo "ERROR: Its needed Python version 2.7 or greater (3.X recomended), not ${pyver}"
                echo "Please, upgrade it."; exit 1
        else
                echo '###########################################################################'
                echo "Please, ensure that this Python modules are available in the local system:"
                echo "sys, optparse, os, sqlite3, datetime, locale, platform"
                echo '###########################################################################'
        fi
fi

F_TMP1=`mktemp -d`
D_BIN='/usr/bin'

echo "Tuptime installation script"
echo ""

echo "Clonning repository..."
git clone https://github.com/rfrail3/tuptime.git ${F_TMP1}

echo "Copying files..."
cp -a ${F_TMP1}/latest/tuptime ${D_BIN}/tuptime
chmod 755 ${D_BIN}/tuptime

systemctl --version &> /dev/null
if [ $? -eq 0 ]; then
	echo "Copying systemd file..."
	cp -a ${F_TMP1}/latest/systemd/tuptime.service  /lib/systemd/system/
	systemctl enable tuptime.service
else
	echo "Copying init file..."
	cp -a ${F_TMP1}/latest/init.d/tuptime.init.d-debian7 /etc/init.d/tuptime
	chmod 755 /etc/init.d/tuptime
	update-rc.d tuptime defaults
fi

echo "Copying cron file..."
cp -a ${F_TMP1}/latest/cron.d/tuptime /etc/cron.d/tuptime

echo "Enjoy!"

tuptime
