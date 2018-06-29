=====================
| Build Tuptime DEB |
=====================


1.- Install dependencies:

    apt-get install dpkg-dev debhelper git

2.- Change to any unprivileged user and create the package. Not build packages using root.

    cd ~
    git clone https://github.com/rfrail3/tuptime.git
    cd tuptime
    dpkg-buildpackage -us -uc

3.- Here is:

    ls ../tuptime-*.deb

4.- As root, install and enable:

    dpkg -i tuptime-*.deb
    systemctl status tuptime.service




Z.- For testing with "dev" branch. Replace step "2" with the following:

    cd ~
    git clone -b dev https://github.com/rfrail3/tuptime.git
    cd tuptime
    dpkg-buildpackage -us -uc
