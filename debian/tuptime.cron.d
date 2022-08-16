# /etc/cron.d/tuptime: crontab entry for tuptime update. 

# NOTE: Decrease the execution time for increase accuracity.


# Skip in favour of systemd timer
[ ! -d /run/systemd/system ] || exit 0

*/5 * * * *   _tuptime    if [ -x /usr/bin/tuptime ]; then /usr/bin/tuptime -x > /dev/null; fi

