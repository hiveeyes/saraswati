.. _setup-docker:

####################
Installing Docker CE
####################


Prepare environment
===================
.. note::

    These steps have been derived from the
    `Installation instructions for Docker CE on Debian`_.
    You can skip these if you already have a working Docker
    setup on your machine.

- Ensure you have at least version 3.10 of the Linux kernel::

    uname -r
    3.16.0-4-amd64

- Add the "Debian backports" release to your ``/etc/apt/sources.list``::

    deb http://ftp.debian.org/debian jessie-backports main

- and install some initial packages::

    apt update
    apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common

- Add Docker’s official GPG key::

    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -


Setup Docker
============
- Finally, add the Docker CE repository::

    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

- and install the software::

    apt update && install docker-ce



Check and configure the Docker setup
====================================
To confirm the Docker installation succeeded and the daemon is running, type::

    docker ps

We want to be able to `manage Docker as a non-root user`_::

    # Add user group for docker
    groupadd docker

    # Add user "workbench" to the "docker" user group
    usermod -aG docker workbench

Verify that you can run docker commands without sudo::

    su - workbench
    docker run hello-world
