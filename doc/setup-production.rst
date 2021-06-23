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

For all of the next steps within this section, please make sure you are
impersonated as user ``saraswati``::

    sudo su - saraswati

Generate a SSH keypair to authenticate with the upload server::

    ssh-keygen -t ed25519

Then, append the public key, ``~/.ssh/id_ed25519.pub``, to the
``/home/foobar/.ssh/authorized_key`` file on the remote file archive server.
You can either do this manually or use the ``ssh-copy-id`` program, like::

    ssh-copy-id foobar@daq.example.org

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

Errors from GStreamer
=====================

GStreamer will signal any errors on audio hardware access, file system access,
or codec and other pipeline errors using an message event system.

Please watch out for GStreamer pipeline errors or warnings in the log output,
those will indicate any problems pretty verbosely, like::

    [saraswati.recorder] WARNING: Pipeline warning:
    gst-resource-error-quark: Could not open audio device for recording. Device is being used by another application. (4)
    (gstalsasrc.c(743): gst_alsasrc_open (): /GstAlsaSrc:autoaudiosrc0-actual-src-als: Device 'default' is busy)

or::

    [saraswati.recorder] ERROR  : Pipeline error:
    gst-resource-error-quark: Could not open file "/path/to/spool/2021/06/23/testdrive/20210623T002844+0000_testdrive_0000.mka" for writing. (6)
    (gstfilesink.c(473): gst_file_sink_open_file (): /GstPipeline:pipeline0/GstSplitMuxSink:muxer/GstFileSink:sink: system error: Bad file descriptor)

Solution: Invoke ``mkdir -p /path/to/spool``.

or::

    gst_parse_error: no element "flacenc" (1)


Networking errors
=================

When trying to upload files to a remote server, ``rsync`` will need a valid SSH
connection. On this matter, a variety of errors might happen. For example::

    [saraswati.uploader] ERROR  : Rsync command failed: ssh: Could not resolve hostname daq.example.org: Name or service not known

Solution: Make sure to configure ``--upload`` or ``SARASWATI_UPLOAD_TARGET`` appropriately.

or::

    [saraswati.uploader] ERROR  : Rsync command failed: Host key verification failed.

Solution: On the audio acquisition system, invoke ``ssh foobar@daq.example.org -o StrictHostKeyChecking=accept-new``
to make sure the SSH connection to the remote server works.

or::

    [saraswati.uploader] ERROR  : Rsync command failed: rsync: change_dir#3 "/tmp/saraswati/testdrive/wp0Kel53aw/area-42" failed: No such file or directory (2)

Solution: On the remote server, invoke ``mkdir -p /tmp/saraswati/testdrive/wp0Kel53aw/area-42``.
