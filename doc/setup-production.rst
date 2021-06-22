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


Configure audio channels
========================

In order to configure more options like adding audio acquisition channels,
adjusting the upload target, etc., please amend the configuration settings
within ``/etc/default/saraswati``. After changing them, please restart the
service using ``systemctl restart saraswati``.

Adding channels will look like::

    # Use real hardware devices
    # SARASWATI_CHANNEL_1='channel1 source=alsasrc device="hw:0"'
    # SARASWATI_CHANNEL_2="channel1 source=pulsesrc device=alsa_input.usb-0c76_USB_Audio_Device-00.mono-fallback"

    # Use sine wave generators
    # SARASWATI_CHANNEL_1="channel1 source=audiotestsrc wave=3 freq=200"
    # SARASWATI_CHANNEL_2="channel2 source=audiotestsrc wave=3 freq=400"

Please note that the suffix to the variable name, ``_1``, ``_2``, will have no
semantic meaning. It is just to tell different ``CHANNEL`` options apart.

In order to find out about hardware devices available to GStreamer, you might
want to invoke ``gst-device-monitor-1.0`` and inspect its output. In the last
line of each section describing a single device, there is an example command
line starting with ``gst-launch-1.0``. What comes right after this command is
the GStreamer source element string to use within the channel definition of
Saraswati, after the ``channel1 source=`` prefix.


Configure file upload
=====================

Currently, uploading using rsync+ssh is supported. The upload target will be
configured like::

    SARASWATI_UPLOAD_TARGET="rsync://foobar@daq.example.org:/var/spool/saraswati/testdrive/wp0Kel53aw/area-42/audionode-01"

After changing this setting, please restart the service using ``systemctl
restart saraswati``.

When generating a SSH keypair to authenticate with the upload server, please
make sure to invoke it as user ``saraswati``::

    sudo su - saraswati
    ssh-keygen -t ed25519

If you need to configure another SSH private key for the connection or want
to adjust the TCP port the remote SSH server is listening on, please edit
your ``~/.ssh/config`` file appropriately by adding such a section::

    Host daq.example.org
      IdentityFile ~/.ssh/id_ed25519
      Port 2222

Also make sure you are doing this as user ``saraswati``, so the effective
file you are editing would be ``/home/saraswati/.ssh/config``.
