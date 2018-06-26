=====================
| Build Tuptime RPM |
=====================


Install dependencies:

    Latest releases of Fedora, RedHat 8, Centos 8:
        yum -y install rpmdevtools git python3 python3-devel

    Older releases of Fedora, Redhat 7, CentOS 7, install from EPEL:
        yum -y install rpmdevtools git python34 python34-devel

Change to any unprivileged user. Not build packages using root.

    cd ~
    git clone https://github.com/rfrail3/tuptime.git

Create the package:

    rpmdev-setuptree
    cp tuptime/misc/rpm/tuptime.spec ~/rpmbuild/SPECS/
    cd ~/rpmbuild/SPECS/
    spectool -g -R tuptime.spec
    rpmbuild -ba --target=noarch tuptime.spec

Here is:

    ls ~/rpmbuild/RPMS/noarch/tuptime-*.rpm

As root, install and enable:

    rpm -i tuptime-*.rpm
    systemctl enable tuptime.service
    systemctl enable tuptime.timer
    systemctl start tuptime.service
    systemctl start tuptime.timer
