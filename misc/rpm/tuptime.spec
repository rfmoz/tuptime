Name:		tuptime
Version:	5.0.2
Release:	1%{?dist}
Summary:	Report historical system real time

License:	GPLv2+
BuildArch:	noarch
URL:		https://github.com/rfrail3/tuptime/
Source0:	https://github.com/rfrail3/tuptime/archive/%{version}.tar.gz

%{?systemd_requires}
# Check for EPEL Python (python34, python36)
%if 0%{?python3_pkgversion}
Requires:	python%{python3_pkgversion}
%else
Requires:	python3
%endif
BuildRequires:	sed python3-rpm-macros python-srpm-macros systemd
Requires:	systemd
Requires(pre):	shadow-utils


%description
Tuptime track and report historical and statistical real time of the
 system, keeping the uptime and downtime between shutdowns.


%prep
%setup -q
# Fix python shebang
sed -i '1s=^#!/usr/bin/\(python\|env python\)[23]\?=#!%{__python3}=' src/tuptime


%pre
getent group tuptime >/dev/null && groupmod -n _tuptime tuptime
getent passwd tuptime >/dev/null && usermod -l _tuptime tuptime
getent group _tuptime >/dev/null || groupadd -r _tuptime
getent passwd _tuptime >/dev/null || useradd --system --gid _tuptime --home-dir "/var/lib/tuptime" --shell '/sbin/nologin' --comment 'Tuptime execution user' _tuptime > /dev/null


%build
exit 0


%install
install -d %{buildroot}%{_bindir}/
install -d %{buildroot}%{_unitdir}/
install -d %{buildroot}%{_mandir}/man1/
install -d %{buildroot}%{_sharedstatedir}/tuptime/
install -d %{buildroot}%{_docdir}/tuptime/
cp -R %{_topdir}/BUILD/%{name}-%{version}/src/tuptime %{buildroot}%{_bindir}/
cp -R %{_topdir}/BUILD/%{name}-%{version}/src/systemd/tuptime.service %{buildroot}%{_unitdir}/
cp -R %{_topdir}/BUILD/%{name}-%{version}/src/systemd/tuptime-cron.service %{buildroot}%{_unitdir}/
cp -R %{_topdir}/BUILD/%{name}-%{version}/src/systemd/tuptime-cron.timer %{buildroot}%{_unitdir}/
cp -R %{_topdir}/BUILD/%{name}-%{version}/src/man/tuptime.1 %{buildroot}%{_mandir}/man1/
cp -R %{_topdir}/BUILD/%{name}-%{version}/tuptime-manual.txt %{buildroot}%{_docdir}/tuptime/
cp -R %{_topdir}/BUILD/%{name}-%{version}/CHANGELOG %{buildroot}%{_docdir}/tuptime/


%post
su -s /bin/sh _tuptime -c "(umask 0022 && /usr/bin/tuptime -x)"
%systemd_post tuptime.service
%systemd_post tuptime-cron.service
%systemd_post tuptime-cron.timer


%preun
%systemd_user_preun tuptime.service
%systemd_user_preun tuptime-cron.service
%systemd_user_preun tuptime-cron.timer


%postun
%systemd_postun_with_restart tuptime.service
%systemd_postun_with_restart tuptime-cron.service
%systemd_postun_with_restart tuptime-cron.timer


%files
%defattr(-,root,root)
%{_unitdir}/tuptime.service
%{_unitdir}/tuptime-cron.service
%{_unitdir}/tuptime-cron.timer
%attr(0755, root, root) %{_bindir}/tuptime
%dir %attr(0755, _tuptime, _tuptime) %{_sharedstatedir}/tuptime/
%docdir %{_docdir}/tuptime/
%{_docdir}/tuptime/tuptime-manual.txt
%{_docdir}/tuptime/CHANGELOG
%{_mandir}/man1/tuptime.1.gz


%changelog
* Sat Jan 02 2021 Ricardo Fraile <rfraile@rfraile.eu> 5.0.2-1
- RPM release
