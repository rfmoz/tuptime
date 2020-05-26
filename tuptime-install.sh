#!/bin/sh

#
# Tuptime installation linux script
# v.1.8.8
#
# Usage:
#	bash tuptime-install.sh		Normal installation
#	bash tuptime-install.sh -d 	Installation using dev branch
#

# Execution user
EXUSR='_tuptime'

# Destination dir for executable file
D_BIN='/usr/bin'

# PID 1 process
PID1=$(grep 'Name' /proc/1/status | cut -f2)

# Swich dev branch
DEV=0


# Check bash execution
if [ ! -n "$BASH" ]; then
  echo "--- WARNING - execute only with BASH ---"
fi

# Check root execution
if [ "$(id -u)" != "0" ]; then
  echo "Please run this script as root"
  exit
fi

# Test arguments
while test $# -gt 0; do
    case "$1" in
        -d) DEV=1
           ;;
    esac
    shift
done

# Test if it is a linux system
if [ "$(expr substr "$(uname -s)" 1 5)" != "Linux" ]; then
	echo "Sorry, only for Linux systems"
	exit 1
fi

# Test if curl is installed
curl --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "ERROR: \"curl\" command not available"
	echo "Please, install it"; exit 1
fi

# Test if tar is installed
tar --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "ERROR: \"tar\" command not available"
	echo "Please, install it"; exit 1
fi

# Test if python is installed
pyver=$(python3 --version 2> /dev/null)
if [ $? -ne 0 ]; then
        echo "ERROR: Python not available"
        echo "Please, install version 3 or greater"; exit 1
else
	# Test if version 3 or avobe of python is installed
	pynum=$(echo "${pyver}" | tr -d '.''' | grep -Eo  '[0-9]*' | head -1 | cut -c 1-2)
        if [ "$pynum" -lt 30 ] ; then
                echo "ERROR: Its needed Python version 3, not ${pyver}"
                echo "Please, upgrade it."; exit 1
        else
		# Test if all modules needed are available
		pymod=$(python3 -c "import sys, os, argparse, locale, platform, signal, logging, sqlite3, datetime")
                if [ $? -ne 0 ]; then
                        echo "ERROR: Please, ensure that these Python modules are available in the local system:"
                        echo "sys, os, optparse, sqlite3, locale, platform, datetime, logging"; exit 1
                fi
        fi
fi

# Set SystemD path
if [ -d /usr/lib/systemd/system/ ]; then
	SYSDPATH='/usr/lib/systemd/system/'
else
	SYSDPATH='/lib/systemd/system/'
fi

# Set Selinux swich
SELX=$(getenforce 2> /dev/null)
if [ "${SELX}" = 'Enforcing' ]; then
        echo "Selinux enabled in Enforcing"
	SELX=1
else
	SELX=0
fi

# Temporary dir to download sources
F_TMP1=$(mktemp -d)

echo ""
echo "++ Tuptime installation script ++"
echo ""

echo "+ Getting source tar file"
if [ ${DEV} -eq 1 ]; then
        echo "  ...using dev branch"
	tar xz --strip 1 -C "${F_TMP1}" -f <(curl -sL https://github.com/rfrail3/tuptime/archive/dev.tar.gz) || exit
else
	tar xz --strip 1 -C "${F_TMP1}" -f <(curl -sL https://github.com/rfrail3/tuptime/archive/master.tar.gz) || exit
fi
echo '  [OK]'

echo "+ Copying files"
install -m 755 "${F_TMP1}"/src/tuptime "${D_BIN}"/tuptime || exit
((SELX)) && restorecon -vF "${D_BIN}"/tuptime
echo '  [OK]'

echo "+ Creating Tuptime execution user '_tuptime'"
useradd -h > /dev/null 2>&1
if [ $? -eq 0 ]; then
	useradd --system --no-create-home --home-dir '/var/lib/tuptime' \
        	--shell '/bin/false' --comment 'Tuptime execution user' "${EXUSR}"
else
	adduser -S -H -h '/var/lib/tuptime' -s '/bin/false' "${EXUSR}"
fi
echo '  [OK]'

echo "+ Creating Tuptime db"
tuptime -x
echo '  [OK]'

echo "+ Setting Tuptime db ownership"
chown -R "${EXUSR}":"${EXUSR}" /var/lib/tuptime || exit
chmod 755 /var/lib/tuptime || exit
echo '  [OK]'

echo "+ Executing Tuptime with '_tuptime' user for testing"
su -s /bin/sh "${EXUSR}" -c "tuptime -x" || exit
echo '  [OK]'

# Install init
if [ "${PID1}" = 'systemd' ]; then
	echo "+ Copying Systemd file"
	cp -a "${F_TMP1}"/src/systemd/tuptime.service "${SYSDPATH}" || exit
	((SELX)) && restorecon -vF "${SYSDPATH}"tuptime.service
	systemctl daemon-reload || exit
	systemctl enable tuptime.service && systemctl start tuptime.service || exit
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /etc/rc.d/init.d/functions ]; then
	echo "+ Copying  SysV init RedHat file"
	install -m 755 "${F_TMP1}"/src/init.d/redhat/tuptime /etc/init.d/tuptime || exit
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	chkconfig --add tuptime || exit
	chkconfig tuptime on || exit
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /lib/lsb/init-functions ]; then
	echo "+ Copying SysV init Debian file"
	install -m 755 "${F_TMP1}"/src/init.d/debian/tuptime /etc/init.d/tuptime || exit
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	update-rc.d tuptime defaults || exit
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /etc/rc.conf ]; then
	echo "+ Copying OpenRC file for init"
	install -m 755 "${F_TMP1}"/src/openrc/tuptime /etc/init.d/ || exit
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	rc-update add tuptime default && rc-service tuptime start || exit
	echo '  [OK]'

elif [ "${PID1}" = 'openrc-init' ]; then
	echo "+ Copying OpenRC file for openrc-init"
	install -m 755 "${F_TMP1}"/src/openrc/tuptime /etc/init.d/ || exit
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	rc-update add tuptime default && rc-service tuptime start || exit
	echo '  [OK]'

elif [ "${PID1}" = 'runit' ] && [ -f /etc/rc.local ] && [ -f /etc/rc.shutdown ]; then
	echo "+ Runit startup and shutdown execution"
	echo 'tuptime -x' >> /etc/rc.local || exit
	echo 'tuptime -gx' >> /etc/rc.shutdown || exit

else
	echo "#########################################"
	echo " WARNING - Any init file for your system"
	echo "#########################################"
	echo '  [BAD]'
fi

# Install cron
if [ -d /etc/cron.d/ ]; then
	echo "+ Copying Cron file"
	cp -a "${F_TMP1}"/src/cron.d/tuptime /etc/cron.d/tuptime || exit
	((SELX)) && restorecon -vF /etc/cron.d/tuptime
	echo '  [OK]'

elif [ -d "${SYSDPATH}" ]; then
	echo "+ Copying tuptime-cron.timer and .service"
	cp -a "${F_TMP1}"/src/systemd/tuptime-cron.*  "${SYSDPATH}" || exit
	((SELX)) && restorecon -vF "${SYSDPATH}"tuptime-cron.*
	systemctl enable tuptime-cron.timer && systemctl start tuptime-cron.timer
	echo '  [OK]'

elif [ -d /etc/cron.hourly/ ]; then
	echo "+ Cron hourly execution"
	printf '#!/bin/sh \n tuptime -x' > /etc/cron.hourly/tuptime || exit
	chmod 744 /etc/cron.hourly/tuptime || exit
	echo '  [OK]'

elif [ -d /etc/periodic/15min/ ]; then
	echo "+ Periodic execution"
	printf '#!/bin/sh \n tuptime -x' > /etc/periodic/15min/tuptime || exit
	chmod 744 /etc/periodic/15min/tuptime || exit
	echo '  [OK]'

else
	echo "#########################################"
	echo " WARNING - Any cron file for your system"
	echo "#########################################"
	echo '  [BAD]'
fi

echo "+ Enjoy!"
echo ""

tuptime
