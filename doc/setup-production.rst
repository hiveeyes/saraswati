###############################
Running Saraswati in production
###############################


Configure system
================

Synchronize system time with NTP, this is important for appropriate timestamping::

    sudo timedatectl set-ntp true


Install Saraswati
=================

Please follow the documentation at https://github.com/hiveeyes/saraswati/tree/0.3.2#install-prerequisites
in order to install required dependencies. Then, invoke::

    sudo pip3 install saraswati --upgrade



Install systemd service
=======================

This will create the system-wide user ``saraswati``, add it to the ``audio``
user group, and copies the configuration file to ``/etc/default/saraswati``.
It also installs a systemd unit file to ``/usr/lib/systemd/system/saraswati.service``.
Afterwards, it will activate and start the service.

The default spool directory, configured in ``/etc/default/saraswati``, is
``/var/spool/saraswati``.

One-step installation for Linux::

    sudo saraswati setup --systemd

Watch log output::

    journalctl --unit=saraswati --follow


Reconfigure settings
====================

In order to configure more options like adding audio acquisition channels,
adjusting the upload target, etc., please amend the configuration settings
within ``/etc/default/saraswati``. After changing them, please restart the
service using ``systemctl restart saraswati``.

Adding channels will look like::

    # Use real hardware devices
    # SARASWATI_CHANNEL_1='channel1 source=alsasrc device="hw:0"'

    # Use sine wave generators
    SARASWATI_CHANNEL_1="channel1 source=audiotestsrc wave=3 freq=200"
    SARASWATI_CHANNEL_2="channel2 source=audiotestsrc wave=3 freq=400"

Please note that the suffix to the variable name, ``_1``, ``_2``, will have no
semantic meaning. It is just to tell different ``CHANNEL`` options apart.

In order to find out about hardware devices available to GStreamer, you
might want to invoke ``gst-device-monitor-1.0`` and inspect its output.
