=====================
| Build Tuptime RPM |
=====================


1.- Install dependencies:

    Latest releases of Fedora, RedHat 8, Centos 8:
        yum -y install rpmdevtools wget python3-rpm-macros python-srpm-macros

    Older releases of Fedora, Redhat 7, CentOS 7, install from EPEL:
        yum -y install rpmdevtools wget python3-rpm-macros python-srpm-macros

2.- Change to any unprivileged user and create the package. Not build packages using root.

    cd ~
    rpmdev-setuptree
    cd ~/rpmbuild/SPECS/
    wget 'https://raw.githubusercontent.com/rfrail3/tuptime/master/misc/rpm/tuptime.spec'
    spectool -g -R tuptime.spec
    rpmbuild -ba --target=noarch tuptime.spec

3.- Here is:

    ls ~/rpmbuild/RPMS/noarch/tuptime-*.rpm

4.- As root, install and enable:

    rpm -i tuptime-*.rpm
    systemctl enable tuptime.service && systemctl start tuptime.service
    systemctl enable tuptime-cron.timer && systemctl start tuptime-cron.timer

5.- Check it all was ok:

    systemctl status tuptime.service
    systemctl status tuptime-cron.timer



Z.- For testing with "dev" branch. Replace step "2" with the following:

    cd ~
    git clone -b dev https://github.com/rfrail3/tuptime.git tuptime-4.0.0
    rpmdev-setuptree
    cd ~/rpmbuild/SPECS/
    cp ../../tuptime-4.0.0/misc/rpm/tuptime.spec .
    tar -czvf ../SOURCES/4.0.0.tar.gz ../../tuptime-4.0.0
    rpmbuild -ba --target=noarch tuptime.spec
