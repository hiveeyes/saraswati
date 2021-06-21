####################
Hacking on Saraswati
####################


Clone source repository
=======================
::

    # Install git
    # {apt-get|brew} install git

    # Run clone process
    git clone https://github.com/hiveeyes/saraswati.git
    cd saraswati

    # Invoke test suite
    make test


Using Docker for development
============================

This will give you a Linux environment, even on non-Linux workstations.

::

    docker build --file=dockerfiles/develop.Dockerfile --tag=saraswati-develop .
    docker run -it --rm --volume=$PWD:/src saraswati-develop bash
    pip3 install --editable=/src
    saraswati record --channel="testdrive source=audiotestsrc wave=3 freq=200"
