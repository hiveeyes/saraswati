###################
Saraswati changelog
###################


in progress
===========

- Add capability for storing audio without putting it into container. Thanks, @MKO1640.
- Add audio formats "wav" and "WavPack". Thanks, @MKO1640.

2021-07-21 0.6.0
================

- Don't automatically start tailing the log file after "saraswati setup"
- Add systemd path-activation file in order to start the Saraswati service only
  after all USB sound devices have been registered by watching ``/dev/bus/usb``.
- Optionally use Ogg container format for audio recordings, by using the option
  ``--container-format=ogg`` or the ``SARASWATI_CONTAINER_FORMAT`` environment
  variable.


2021-06-23 0.5.0
================

- Run recorder service task (checking for free disk space) each 10 seconds
- Improve production setup documentation
- Remove ``recording_`` prefix from recorded file name. Thanks, @msweef.
- Improve spool subdirectory hierarchy to reduce the number of files per directory. Thanks, Michael.
  The new scheme is ``/var/spool/saraswati/{year}/{month:02d}/{day:02d}/{channel}/{timestamp}_{channel}_{fragment:04d}.mka``.
- Use more ISO-like timestamp format, separating each datetime's fragments.
  Currently, ``%Y-%m-%dT%H-%M-%S%z`` is used.
- Improve error handling on exceptions from "on_format_location" callbacks


2021-06-22 0.4.2
================

- Improve user creation and production setup documentation


2021-06-22 0.4.1
================

- Improve production setup documentation


2021-06-22 0.4.0
================

- Prepare Saraswati to run as system service. There is now a corresponding
  command ``sudo saraswati setup --systemd`` which aids this.
- Emit warning when no audio pipelines are defined


2021-06-21 0.3.2
================

- Improve logging: Emit ``Gst.MessageType.WARNING`` messages from GStreamer pipelines


2021-06-21 0.3.1
================

- Add guidelines for running Saraswati on Docker
- Fix program flow when no ``--upload`` option is given


2021-06-21 0.3.0
================

- Use 5 minutes recording chunk size as default
- Protect against running out of disk space
- Add uploader based on ``rsync``. Thanks Roh and Diren!


2021-06-20 0.2.0
================

- Adjust recording pipeline: Add ``audioconvert ! queue`` GStreamer elements after audio source
- Improve documentation
- Fix creating spool directory
- Improve installation convenience by not depending on ``PyGObject-stubs`` at runtime


2021-06-20 0.1.0
================

- Add project infrastructure
- Adjust to API of GStreamer 1.18.4
- Run software tests on CI/GHA
- Refactor recorder program into "saraswati" module
- Use ISO8601-like timestamps again
- Significantly improve package and program structure
- Make all relevant parameters configurable
- Add command line entrypoint ``saraswati``. Invoke ``saraswati --help`` in
  order to find out about its usage.
- Improve documentation
- Add ``CHANGES.rst``
- Ensure spool directory exists by automatically creating it
- Fix selecting a custom recording location (--spool)


2019-10-10 0.0.0
================

- Acquire audio from four channels, use accurate timestamp, add server transfer. Thanks, Diren!


2018-11-03 0.0.0
================

- Add basic example for demonstrating the GStreamer Python bindings
- Honor GStreamer 1.10.4
- Store audio chunks to /var/spool/saraswati
- Use chunk length of 10 seconds
- Run on BeagleBone
- Use ``.mka`` as filename extension for audio-only Matroska files
