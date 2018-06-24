=====================
| Build Tuptime RPM |
=====================


Install dependencies:

    yum -y install rpmdevtools git python3-devel

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

    ls ~/rpmbuild/RPMS/noarch/tuptime*.rpm
    cp ~/rpmbuild/RPMS/noarch/tuptime*.rpm /tmp/

Install and enable as root:

    rpm -i /tmp/tuptime*.rpm
    systemctl enable tuptime.service
    systemctl enable tuptime.tiimer
    systemctl start tuptime.service
    systemctl start tuptime.timer
