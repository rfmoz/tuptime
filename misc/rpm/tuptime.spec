Name:		tuptime
Version:	5.2.1
Release:	1%{?dist}
Summary:	Report historical system real time

License:	GPLv2+
BuildArch:	noarch
URL:		https://github.com/rfrail3/tuptime/
Source0:	https://github.com/rfrail3/tuptime/archive/%{version}.tar.gz

%{?systemd_requires}
# Check for EPEL Python (python34, python36)
%if 0%{?python3_pkgversion}
BuildRequires:	python%{python3_pkgversion}-devel
%else
BuildRequires:	python3-devel
%endif
%if 0%{?el7}
BuildRequires:	systemd
%else
BuildRequires:	systemd-rpm-macros
%endif
Requires:	systemd
Requires(pre):	shadow-utils


%description
Tuptime track and report historical and statistical real time of the
system, keeping the uptime and downtime between shutdowns.


%prep
%setup -q
# Fix python shebang
%if %{?py3_shebang_fix:1}%{!?py3_shebang_fix:0}
%py3_shebang_fix src/tuptime
%else
# EPEL7 does not have py3_shebang_fix
/usr/bin/pathfix.py -pni "%{__python3} -s" src/tuptime
%endif


%pre
# Conversion to new group and usernames for previously installed version
getent group tuptime >/dev/null && groupmod --new-name _tuptime tuptime
getent passwd tuptime >/dev/null && usermod --login _tuptime tuptime
getent group _tuptime >/dev/null || groupadd --system _tuptime
getent passwd _tuptime >/dev/null || useradd --system --gid _tuptime --home-dir "/var/lib/tuptime" --shell '/sbin/nologin' --comment 'Tuptime execution user' _tuptime > /dev/null


%build


%install
install -d %{buildroot}%{_bindir}/
install -d %{buildroot}%{_unitdir}/
install -d %{buildroot}%{_mandir}/man1/
install -d %{buildroot}%{_sharedstatedir}/tuptime/
install -d %{buildroot}%{_datadir}/tuptime/
cp src/tuptime %{buildroot}%{_bindir}/
cp src/systemd/tuptime.service %{buildroot}%{_unitdir}/
cp src/systemd/tuptime-sync.service %{buildroot}%{_unitdir}/
cp src/systemd/tuptime-sync.timer %{buildroot}%{_unitdir}/
cp src/man/tuptime.1 %{buildroot}%{_mandir}/man1/
cp misc/scripts/* %{buildroot}%{_datadir}/tuptime/
chmod +x %{buildroot}%{_datadir}/tuptime/*.sh
chmod +x %{buildroot}%{_datadir}/tuptime/*.py


%post
# Create and initialise the tuptime DB with consistent permissions, etc.
su -s /bin/sh _tuptime -c "(umask 0022 && /usr/bin/tuptime -x)"
%systemd_post tuptime.service
%systemd_post tuptime-sync.service
%systemd_post tuptime-sync.timer


%preun
%systemd_preun tuptime.service
%systemd_preun tuptime-sync.service
%systemd_preun tuptime-sync.timer


%postun
%systemd_postun_with_restart tuptime.service
%systemd_postun_with_restart tuptime-sync.service
%systemd_postun_with_restart tuptime-sync.timer


%files
%{_unitdir}/tuptime.service
%{_unitdir}/tuptime-sync.service
%{_unitdir}/tuptime-sync.timer
%attr(0755, root, root) %{_bindir}/tuptime
%dir %attr(0755, _tuptime, _tuptime) %{_sharedstatedir}/tuptime/
%doc tuptime-manual.txt
%doc CHANGELOG README.md CONTRIBUTING.md
%license LICENSE
%{_mandir}/man1/tuptime.1.*
%dir %{_datadir}/tuptime
%{_datadir}/tuptime/*


%changelog
* Fri Aug 19 2022 Ricardo Fraile <rfraile@rfraile.eu> 5.2.1-1
- New release

* Mon Aug 15 2022 Ricardo Fraile <rfraile@rfraile.eu> 5.2.0-1
- New release

* Sun Jan 16 2022 Ricardo Fraile <rfraile@rfraile.eu> 5.1.0-1
- Bump new release

* Thu Jan 06 2022 Frank Crawford <frank@crawford.emu.id.au> 5.0.2-5
- First offical release in Fedora

* Tue Jan 04 2022 Frank Crawford <frank@crawford.emu.id.au> 5.0.2-4
- Futher updates to spec file following review comments

* Mon Dec 13 2021 Frank Crawford <frank@crawford.emu.id.au> 5.0.2-3
- Update spec file following review comments

* Sun Sep 26 2021 Frank Crawford <frank@crawford.emu.id.au> 5.0.2-2
- Update spec file for Fedora package review
- Copy all relevant documentation

* Sat Jan 02 2021 Ricardo Fraile <rfraile@rfraile.eu> 5.0.2-1
- RPM release
