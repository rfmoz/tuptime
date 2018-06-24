=====================
| Build Tuptime RPM |
=====================


Install dependencies:

    yum -y install rpmdevtools git

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
