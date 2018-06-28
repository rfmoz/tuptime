=====================
| Build Tuptime RPM |
=====================


Install dependencies:

    Latest releases of Fedora, RedHat 8, Centos 8:
        yum -y install rpmdevtools wget python3-rpm-macros python-srpm-macros

    Older releases of Fedora, Redhat 7, CentOS 7, install from EPEL:
        yum -y install rpmdevtools wget python3-rpm-macros python-srpm-macros

Change to any unprivileged user and create the package. Not build packages using root.

    cd ~
    rpmdev-setuptree
    cd ~/rpmbuild/SPECS/
    wget 'https://raw.githubusercontent.com/rfrail3/tuptime/master/misc/rpm/tuptime.spec'
    # Dev branch --> wget 'https://raw.githubusercontent.com/rfrail3/tuptime/dev/misc/rpm/tuptime.spec'
    spectool -g -R tuptime.spec
    rpmbuild -ba --target=noarch tuptime.spec

Here is:

    ls ~/rpmbuild/RPMS/noarch/tuptime-*.rpm

As root, install and enable:

    rpm -i tuptime-*.rpm
    systemctl enable tuptime.service
    systemctl enable tuptime-cron.timer
    systemctl start tuptime.service
    systemctl start tuptime-cron.timer
