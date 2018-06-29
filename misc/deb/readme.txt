=====================
| Build Tuptime DEB |
=====================


Install dependencies:

    apt-get install dpkg-dev debhelper git

Change to any unprivileged user and create the package. Not build packages using root.

    cd ~
    git clone https://github.com/rfrail3/tuptime.git
    cd tuptime
    dpkg-buildpackage -us -uc

Here is:

    ls ../tuptime-*.deb

As root, install and enable:

    dpkg -i tuptime-*.deb
    systemctl status tuptime.service
