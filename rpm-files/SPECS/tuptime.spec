Name: tuptime
Version: 3.2.01
Release: 2
Summary: Report the historical and statistical running time of the system, keeping it between restarts.
Packager: Ricardo F.

Group: Applications/System
License: GPL3
URL: https://github.com/rfrail3/tuptime
Source: %{name}-%{version}.tar.gz

Requires: python, systemd
BuildArch: noarch

%description
Tuptime is a tool for report the historical and statistical running time of 
the system, keeping it between restarts.

%prep
%setup -q

%build

%install
#ROOT="$RPM_BUILD_ROOT"
rm -rf %{buildroot}
install -m 755 -d $RPM_BUILD_ROOT/usr/bin/
install -m 755 -d $RPM_BUILD_ROOT/lib/systemd/system/
install -m 755 -d $RPM_BUILD_ROOT/etc/cron.d/
install -m 755 -d $RPM_BUILD_ROOT/usr/share/doc/tuptime/
install -m 755 -d $RPM_BUILD_ROOT/usr/share/man/man1/

install -m 755 usr/bin/tuptime $RPM_BUILD_ROOT/usr/bin/tuptime
install -m 644 lib/systemd/system/tuptime.service $RPM_BUILD_ROOT/lib/systemd/system/tuptime.service
install -m 644 etc/cron.d/tuptime $RPM_BUILD_ROOT/etc/cron.d/tuptime
install -m 644 usr/share/doc/tuptime/tuptime-manual.txt.gz $RPM_BUILD_ROOT/usr/share/doc/tuptime/tuptime-manual.txt.gz
install -m 644 usr/share/man/man1/tuptime.1.gz $RPM_BUILD_ROOT/usr/share/man/man1/tuptime.1.gz

%post
if [ -f "/lib/systemd/system/tuptime.service" ]; then
        systemctl enable tuptime.service
        systemctl start tuptime.service
fi
tuptime -x

%preun
if [ -f "/lib/systemd/system/tuptime.service" ]; then
        systemctl stop tuptime.service
        systemctl disable tuptime.service
fi

%postun
if [ -d "/var/lib/tuptime/" ]; then
        rm -rf /var/lib/tuptime/
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/usr/bin/tuptime
/lib/systemd/system/tuptime.service
/etc/cron.d/tuptime
/usr/share/doc/tuptime/tuptime-manual.txt.gz
/usr/share/man/man1/tuptime.1.gz

%changelog
* Mon Oct 12 2015 Ricardo F. <rfraile@rfraile.eu> - 3.2.01
- Detect database modification

* Mon Oct 05 2015 Ricardo F. <rfraile@rfraile.eu> - 3.2.00
- Print singular names if is the case
- Fix round and decimals values
- Clean and order code

* Mon Sep 28 2015 Ricardo F. <rfraile@rfraile.eu> - 3.1.00
- Register used kernels
- Adding kernel option

* Fri Sep 25 2015 Ricardo F. <rfraile@rfraile.eu> - 3.0.00
- Change printed output format
- Adding max/min uptime/downtime reports
- Adding table format output
- Rename enumerate option to list and change output format
- Adding sorting options
- Change database schema
- Clean and order code

* Mon Aug 10 2015 Ricardo F. <rfraile@rfraile.eu> - 2.6.10
- Compatibility between python2.7 and python3.X
- Removing unused modules

* Sat Aug 08 2015 Ricardo F. <rfraile@rfraile.eu> - 2.5.20
- Setting data type for ok/bad shutdown in db creation

* Fri Aug 07 2015 Ricardo F. <rfraile@rfraile.eu> - 2.5.12
- Setting max decimals in the output
- Fix data type for the ok/bad shutdown registry in db wich cause incorrect
  counter output

* Tue Aug 04 2015 Ricardo F. <rfraile@rfraile.eu> - 2.5.00
- Fix false shutdown count and correct locale date format
- Fix from other point of view false shutdown bug

* Sun Jul 26 2015 Ricardo F. <rfraile@rfraile.eu> - 2.4.10
- Fix false wrong shutdown bug when some kernels rarely report +1 or -1
  second inside /proc/stat btime variable

* Mon Jul 20 2015 Ricardo F. <rfraile@rfraile.eu> - 2.4.00
- Adding downtimes reports
- Adding enumerate option
- Fix bad shutdowns count

* Wed May 06 2015 Ricardo F. <rfraile@rfraile.eu> - 2.2.00
- Completely rewritten in python

* Tue May 14 2013 Ricardo F. <rfraile@rfraile.eu> - 1.6.2
- New init script for debian 7 wheezy

* Sat Nov 17 2012 Ricardo F. <rfraile@rfraile.eu> - 1.6.0
- Remove usage of syslog for more quick output
- Change output
- Print rate in output

* Wed Oct 10 2012 Ricardo F. <rfraile@rfraile.eu> - 1.5.0
- Print estimated uptime between starts
- Print actual uptime for the system
- Fix and improve code, remove repetitive lines and minnor bugs
- Check if the variable in the conf file is a number
- Start using Scalar::Util module
- Print system uptime date
- Fix bug in first update

* Mon Aug 06 2012 Ricardo F. <rfraile@rfraile.eu> - 1.4.0
- Print time more accurate
- Cron line change to 5 minutes
- Print time values in live time without update

* Mon Jun 20 2011 Ricardo F. <rfraile@rfraile.eu> - 1.3.0
- Jump blank lines in conf file
- Adding #REPLACEAT feature

* Mon Jun 13 2011 Ricardo F. <rfraile@rfraile.eu> - 1.2.0
- Change speak option to verbose
- Fix lost information in files when update
- Minnor corrections in text strings

* Fri Jun 10 2011 Ricardo F. <rfraile@rfraile.eu> - 1.1.0
- Any user can print the times, not only root
- Minnor changes to speak option
- Minnor corrections

* Wed Mar 23 2011 Ricardo F. <rfraile@rfraile.eu> - 1.0.0
- First release.
