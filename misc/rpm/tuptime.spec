Name:		tuptime
Version:	5.2.6
Release:	1%{?dist}
Summary:	Report historical system real time

License:	GPL-2.0-or-later
BuildArch:	noarch
URL:		https://github.com/rfmoz/tuptime/
Source0:	https://github.com/rfmoz/tuptime/archive/%{version}.tar.gz

%{?systemd_requires}
# Check for EPEL Python (python34, python36)
%if 0%{?python3_pkgversion}
BuildRequires:	python%{python3_pkgversion}-devel
%else
BuildRequires:	python3-devel
%endif
BuildRequires:	systemd-rpm-macros
Requires:	systemd


%description
Tuptime track and report historical and statistical real time of the
system, keeping the uptime and downtime between shutdowns.


%prep
%autosetup
# Fix python shebang
%py3_shebang_fix src/tuptime


%build


%install
install -d %{buildroot}%{_bindir}/
install -d %{buildroot}%{_unitdir}/
install -d %{buildroot}%{_mandir}/man1/
install -d %{buildroot}%{_sharedstatedir}/tuptime/
install -d %{buildroot}%{_sysusersdir}/
cp src/tuptime %{buildroot}%{_bindir}/
cp src/systemd/tuptime.service %{buildroot}%{_unitdir}/
cp src/systemd/tuptime-sync.service %{buildroot}%{_unitdir}/
cp src/systemd/tuptime-sync.timer %{buildroot}%{_unitdir}/
cp src/systemd/sysusers.d/tuptime.conf %{buildroot}%{_sysusersdir}/
cp src/man/tuptime.1 %{buildroot}%{_mandir}/man1/


%post
%systemd_post tuptime.service
%systemd_post tuptime-sync.service
%systemd_post tuptime-sync.timer
#su -s /bin/sh _tuptime -c "(umask 0022 && /usr/bin/tuptime -q)"


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
%{_sysusersdir}/tuptime.conf
%attr(0755, root, root) %{_bindir}/tuptime
%dir %attr(0755, _tuptime, _tuptime) %{_sharedstatedir}/tuptime/
%doc tuptime-manual.txt
%doc CHANGELOG README.md CONTRIBUTING.md
%license LICENSE
%{_mandir}/man1/tuptime.1.*


%changelog
* Wed Apr 01 2026 Ricardo Fraile <rfraile@rfraile.eu> 5.2.6-1
- RPM release
