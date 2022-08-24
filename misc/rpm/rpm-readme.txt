=====================
| Build Tuptime RPM |
=====================


1.- Install dependencies:

    Latest releases of Fedora, RedHat 8, Centos 8:
        dnf -y install rpmdevtools wget python3-rpm-macros python-srpm-macros rpmlint systemd python3-devel

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

    dnf install tuptime-*rpm   # (old way: rpm -i tuptime-*.rpm)
    systemctl enable tuptime.service && systemctl start tuptime.service
    systemctl enable tuptime-sync.timer && systemctl start tuptime-sync.timer

5.- Check it all was ok:

    systemctl status tuptime.service
    systemctl status tuptime-sync.timer



Z.- For testing with "dev" branch. Install "git" on step "1" and replace step "2" with the following:

    dnf -y install git
    cd ~
    git clone -b dev --depth=1 https://github.com/rfrail3/tuptime.git tuptime-5.2.2
    rpmdev-setuptree
    cd ~/rpmbuild/SPECS/
    cp ../../tuptime-5.2.2/misc/rpm/tuptime.spec .
    tar -czvf ../SOURCES/5.2.2.tar.gz ../../tuptime-5.2.2
    rpmbuild -ba --target=noarch tuptime.spec
