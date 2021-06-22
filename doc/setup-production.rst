###############################
Running Saraswati in production
###############################


*****************
System-wide setup
*****************

Timekeeping
===========

Synchronize system time with NTP, this is important for appropriate timestamping::

    sudo timedatectl set-ntp true


Install Saraswati
=================

Please follow the documentation at https://github.com/hiveeyes/saraswati/tree/0.3.2#install-prerequisites
in order to install required dependencies. Then, invoke::

    sudo pip3 install saraswati --upgrade


Install systemd service
=======================

There is a convenience command ``saraswati setup`` which will create the
system-wide user ``saraswati``, add it to the ``audio`` user group, and copies
a blueprint configuration file to ``/etc/default/saraswati``, if that file does
not exist yet.

It also installs a systemd unit file to ``/usr/lib/systemd/system/saraswati.service``.
Afterwards, it will activate and start the service.

The default spool directory, configured in ``/etc/default/saraswati``, is
``/var/spool/saraswati``.

One-step installation for Linux::

    sudo saraswati setup --systemd

Watch log output::

    journalctl --unit=saraswati --follow


*************
Configuration
*************

In order to configure Saraswati, like adding audio acquisition channels,
adjusting the upload target, etc., please amend the configuration settings
within ``/etc/default/saraswati``. After changing them, please restart the
service using ``systemctl restart saraswati``.


Configure audio channels
========================

Adding channels will look like::

    # Use real hardware devices
    # SARASWATI_CHANNEL_1='channel1 source=alsasrc device="hw:0"'
    # SARASWATI_CHANNEL_2="channel1 source=pulsesrc device=alsa_input.usb-0c76_USB_Audio_Device-00.mono-fallback"

    # Use sine wave generators
    # SARASWATI_CHANNEL_1="channel1 source=audiotestsrc wave=3 freq=200"
    # SARASWATI_CHANNEL_2="channel2 source=audiotestsrc wave=3 freq=400"

Please note that the suffix to the variable name, ``_1``, ``_2``, will have no
semantic meaning. It is just to tell different ``CHANNEL`` options apart.

Find available devices
----------------------

In order to find out about hardware devices available to GStreamer, you might
want to invoke ``gst-device-monitor-1.0`` and inspect its output. In the last
line of each section describing a single device, there is an example command
line starting with ``gst-launch-1.0``. What comes right after this command is
the GStreamer source element string to use within the channel definition of
Saraswati, after the ``channel1 source=`` prefix.

To get a compact output of the information you are looking for here, invoke::

    gst-device-monitor-1.0 | grep gst-launch


Configure spool directory
=========================

By default, the spool directory is ``/var/spool/saraswati``. Please carefully
consider our recommendations when running Saraswati in production.

When this directory is located on the SD card the system is running from, the
data churn happening there will significantly contribute to the flash storage
wearing out, which will eventually render the system defunct after some cycles.

So, you should either locate Saraswati's spool directory on an external disk,
or use a RAM disk.

Please also note that Saraswati runs checks each 10 seconds to prevent running
out of disk space. By default, it will suspend recording if the disk space
available on the device where its spool directory is located, will be less than
10% of its total size.

Using a RAM disk
----------------

To make Saraswati use a part of the system memory for buffering audio data,
create a disk block device based on a RAM disk, like::

    sudo mkdir -p /tmp/ramdisk
    sudo chmod 777 /tmp/ramdisk
    sudo mount -t tmpfs -o size=512m,remount saraswati-spool /tmp/ramdisk

On systems with more memory, use e.g.::

    sudo mount -t tmpfs -o size=4G,remount saraswati-spool /tmp/ramdisk

Then, configure the spool directory like::

    SARASWATI_SPOOL_PATH=/tmp/ramdisk


Configure file upload
=====================

Currently, only uploading using rsync+ssh is supported. The upload target will
be configured like::

    SARASWATI_UPLOAD_TARGET="rsync://foobar@daq.example.org:/var/spool/saraswati/testdrive/wp0Kel53aw/area-42/audionode-01"


Prepare SSH connection
----------------------

For the next steps, please make sure you are impersonated as user ``saraswati``::

    sudo su - saraswati

Generate a SSH keypair to authenticate with the upload server::

    ssh-keygen -t ed25519

If you need to configure another SSH private key for the connection or want
to adjust the TCP port the remote SSH server is listening on, please edit
your ``~/.ssh/config`` file appropriately by adding such a section::

    Host daq.example.org
      IdentityFile ~/.ssh/id_ed25519
      Port 2222

The effective file you are editing would be ``/home/saraswati/.ssh/config``.

In order to check if the connection works, and in order to accept the host key
of the remote host, invoke this command at least once::

    ssh foobar@daq.example.org -o StrictHostKeyChecking=accept-new

Otherwise, Saraswati would not know how to answer that interactive prompt when
connecting to the remote host through ``rsync`` for the very first time::

    Are you sure you want to continue connecting (yes/no)?

The uploader would be blocked here.


***************
Troubleshooting
***************

Recordings are completely silent
================================

If you observe that you will only record silence, please check if the volume
of the hardware device is not turned down completely.

On a Linux terminal, you might want to use the ``alsamixer`` program for that.
On a macOS system, please navigate to "System Preferences » Security & Privacy
» Privacy". There, when selecting "Microphone" on the left hand side, make sure
"Terminal" or "iTerm" is permitted access on the right hand side.

Hardware access or codec errors
===============================

Please watch out for GStreamer pipeline errors or warnings in the log output,
those will indicate any problems pretty verbosely, like::

    [saraswati.recorder]
    WARNING: Pipeline warning: gst-resource-error-quark:
    Could not open audio device for recording. Device is being used by another application. (4)
    (gstalsasrc.c(743): gst_alsasrc_open (): /GstAlsaSrc:autoaudiosrc0-actual-src-als: Device 'default' is busy)

or::

    gst_parse_error: no element "flacenc" (1)
