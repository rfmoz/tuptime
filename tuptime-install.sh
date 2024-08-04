#!/bin/bash
set -e

#
# Tuptime installation linux script
#
# Usage:
# 	 bash tuptime-install.sh	Default master install
# 	 bash tuptime-install.sh -d	Install using dev branch
#

VERSION=1.9.3

# Execution user
EXUSR='_tuptime'

# Destination dir for executable file
D_BIN='/usr/bin'

# Swich dev branch
DEV=0


# Check bash execution
if [ -z "$BASH" ]; then
	echo "--- ERROR - execute only with BASH ---"
	exit 1
fi

# Check root execution
if [ "$(id -u)" != "0" ]; then
	echo "Please run this script as root"
	exit 1
fi

# Test arguments
while getopts ":d" opt; do
	case $opt in
	d)
		DEV=1
		;;
	\?)
		echo "Invalid option: -$OPTARG"
		exit 1
		;;
	esac
done

# Test if it is a linux system
if [ $(uname -s) != "Linux" ]; then
	echo "Sorry, only for Linux systems"
	exit 1
fi

# Test required commands
check_command() {
	if ! command -v "$1" &> /dev/null; then
		echo "ERROR: "$1" command not found"
		echo "Please install it"
		exit 1
	fi
}

check_command "curl"
check_command "tar"
check_command "python3"

# Test python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
if [[ "$(cut -d'.' -f1 <<<"$PYTHON_VERSION")" -lt 3 ]]; then
	echo "ERROR: Python 3 or later is required"
	echo "Please upgrade your Python installation"
	exit 1
else
	# Test if all modules needed are available
	REQUIRED_PYTHON_MODULES=("sys" "os" "argparse" "locale" "platform" "signal" "logging" "sqlite3" "datetime")
	for module in "${REQUIRED_PYTHON_MODULES[@]}"; do
		if ! python3 -c "import $module" &> /dev/null; then
			echo "ERROR: Required Python module '$module' is not available."
			exit 1
		fi
	done
fi

# Set SystemD path
if [ -d /usr/lib/systemd/system/ ]; then
	SYSDPATH='/usr/lib/systemd/system/'
else
	SYSDPATH='/lib/systemd/system/'
fi

# Set Selinux swich
if getenforce 2> /dev/null | grep -q 'Enforcing'; then
       	echo "Selinux enabled in Enforcing"
	SELX=1
else
	SELX=0
fi

# Temporary dir to download sources
F_TMP1=$(mktemp -d)

echo ""
echo "++ Tuptime installation script v.$VERSION ++"
echo ""

echo "+ Getting source tar file"
if [ ${DEV} -eq 1 ]; then
	echo "  ...using dev branch"
	tar xz --strip 1 -C "${F_TMP1}" -f <(curl -sL https://github.com/rfmoz/tuptime/archive/dev.tar.gz)
else
	tar xz --strip 1 -C "${F_TMP1}" -f <(curl -sL https://github.com/rfmoz/tuptime/archive/master.tar.gz)
fi
echo '  [OK]'

echo "+ Copying files"
install -m 755 "${F_TMP1}"/src/tuptime "${D_BIN}"/tuptime
((SELX)) && restorecon -vF "${D_BIN}"/tuptime
echo '  [OK]'

echo "+ Creating Tuptime execution user '_tuptime'"
if systemd-sysusers --version > /dev/null 2>&1; then
	echo "  ...using systemd-sysusers"
        install -m 644 "${F_TMP1}"/src/systemd/sysusers.d/tuptime.conf /usr/lib/sysusers.d/
        ((SELX)) && restorecon -vF /usr/lib/sysusers.d/tuptime.conf
	systemd-sysusers /usr/lib/sysusers.d/tuptime.conf
	echo '  [OK]'

elif useradd -h > /dev/null 2>&1; then
	echo "  ...using useradd"
	useradd --system --no-create-home --home-dir '/var/lib/tuptime' \
        	--shell '/bin/false' --comment 'Tuptime execution user' "${EXUSR}" && echo '  [OK]'
elif adduser -h > /dev/null 2>&1; then
	echo "  ...using adduser"
	adduser -S -H -h '/var/lib/tuptime' -s '/bin/false' "${EXUSR}" && echo '  [OK]'
else
	echo "#######################################"
	echo " WARNING - _tuptime user not available"
	echo "#######################################"
	echo '  [BAD]'
fi

echo "+ Creating Tuptime db"
tuptime -q
echo '  [OK]'

echo "+ Setting Tuptime db ownership"
chown -R "${EXUSR}":"${EXUSR}" /var/lib/tuptime || chown -R "${EXUSR}" /var/lib/tuptime
chmod 755 /var/lib/tuptime
echo '  [OK]'

echo "+ Executing Tuptime with '_tuptime' user for testing"
su -s /bin/sh "${EXUSR}" -c "tuptime -q"
echo '  [OK]'

# Install init
PID1=$(grep 'Name' /proc/1/status | cut -f2)
if [ "${PID1}" = 'systemd' ]; then
	echo "+ Copying Systemd file"
	install -m 644 "${F_TMP1}"/src/systemd/tuptime.service "${SYSDPATH}"
	((SELX)) && restorecon -vF "${SYSDPATH}"tuptime.service
	systemctl daemon-reload
	systemctl enable tuptime.service
	systemctl start tuptime.service
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /etc/rc.d/init.d/functions ]; then
	echo "+ Copying  SysV init RedHat file"
	install -m 755 "${F_TMP1}"/src/init.d/redhat/tuptime /etc/init.d/tuptime
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	chkconfig --add tuptime
	chkconfig tuptime on
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /lib/lsb/init-functions ]; then
	echo "+ Copying SysV init Debian file"
	install -m 755 "${F_TMP1}"/src/init.d/debian/tuptime /etc/init.d/tuptime
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	update-rc.d tuptime defaults
	echo '  [OK]'

elif [ "${PID1}" = 'init' ] && [ -f /etc/rc.conf ]; then
	echo "+ Copying OpenRC file for init"
	install -m 755 "${F_TMP1}"/src/openrc/tuptime /etc/init.d/
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	rc-update add tuptime default
	rc-service tuptime start
	echo '  [OK]'

elif [ "${PID1}" = 'openrc-init' ]; then
	echo "+ Copying OpenRC file for openrc-init"
	install -m 755 "${F_TMP1}"/src/openrc/tuptime /etc/init.d/
	((SELX)) && restorecon -vF /etc/init.d/tuptime
	rc-update add tuptime default
	rc-service tuptime start
	echo '  [OK]'

elif [ "${PID1}" = 'runit' ]; then
	echo "+ Runit startup and shutdown execution"
	install -d -m 755 /etc/sv/tuptime
	install -m 755 "${F_TMP1}"/src/runit/* /etc/sv/tuptime/
	if [ ! -L /etc/service/tuptime ]; then
		ln -s /etc/sv/tuptime/ /etc/service/tuptime
	fi
	sv start tuptime
else
	echo "#########################################"
	echo " WARNING - Any init file for your system"
	echo "#########################################"
	echo '  [BAD]'
fi

# Install cron
if [ -d "${SYSDPATH}" ]; then
	echo "+ Copying tuptime-sync.timer and .service"
	install -m 644 "${F_TMP1}"/src/systemd/tuptime-sync.*  "${SYSDPATH}"
	((SELX)) && restorecon -vF "${SYSDPATH}"tuptime-sync.*
	systemctl enable tuptime-sync.timer
	systemctl start tuptime-sync.timer
	echo '  [OK]'

elif [ -d /etc/cron.d/ ]; then
	echo "+ Copying Cron file"
	install -m 644 "${F_TMP1}"/src/cron.d/tuptime /etc/cron.d/tuptime
	((SELX)) && restorecon -vF /etc/cron.d/tuptime
	echo '  [OK]'

elif [ -d /etc/cron.hourly/ ]; then
	echo "+ Cron hourly execution"
	printf '#!/bin/sh \n tuptime -q' > /etc/cron.hourly/tuptime
	chmod 744 /etc/cron.hourly/tuptime
	echo '  [OK]'

elif [ -d /etc/periodic/15min/ ]; then
	echo "+ Periodic execution"
	printf '#!/bin/sh \n tuptime -q' > /etc/periodic/15min/tuptime
	chmod 744 /etc/periodic/15min/tuptime
	echo '  [OK]'

else
	echo "#########################################"
	echo " WARNING - Any cron file for your system"
	echo "#########################################"
	echo '  [BAD]'
fi

echo "+ Finished, all steps done."
echo ""

tuptime
