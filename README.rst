.. image:: https://github.com/hiveeyes/saraswati/workflows/Tests/badge.svg
    :target: https://github.com/hiveeyes/saraswati/actions?workflow=Tests

.. image:: https://codecov.io/gh/hiveeyes/saraswati/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/hiveeyes/saraswati

.. image:: https://img.shields.io/pypi/pyversions/saraswati.svg
    :target: https://pypi.org/project/saraswati/

.. image:: https://img.shields.io/pypi/v/saraswati.svg
    :target: https://pypi.org/project/saraswati/

.. image:: https://img.shields.io/pypi/l/saraswati.svg
    :alt: License
    :target: https://pypi.org/project/saraswati/

.. image:: https://img.shields.io/pypi/status/saraswati.svg
    :target: https://pypi.org/project/saraswati/

|

#########
Saraswati
#########


*****
About
*****
Saraswati is a robust, multi-channel audio recording,
transmission and storage system.

It is designed to run on `Single-board computer (SBC)`_
systems as well as larger machines.

It might become the designated work horse for flexible field
recording of audio signals in environmental monitoring systems.

We are an open community of scientists from different domains
working collaboratively on this project. You are welcome to
join our efforts.


*********
Etymology
*********
`Saraswati <https://en.wikipedia.org/wiki/Saraswati>`_ is the
Hindu goddess of knowledge, music, art, wisdom and learning.


**********
Background
**********
This software gets developed for the "Bee Observer" (BOB) project,
a joint endeavour initiated by the
`Cognitive neuroinformatics group at the University of Bremen <http://www.cognitive-neuroinformatics.com/en/>`_
and the people of the independent research and development project
`Hiveeyes <https://hiveeyes.org/>`_, see also:

- `hiverize.org - Vernetzt. Smart. Imkern. <https://hiverize.org/>`_
- `The Hiveeyes Project <https://hiveeyes.org/>`_
- `Uni Bremen und Hiveeyes werden als Citizen-Science-Projekte vom Forschungsministerium unterstützt <https://community.hiveeyes.org/t/bee-observer-bob-uni-bremen-und-hiveeyes-werden-als-citizen-science-projekte-vom-forschungsministerium-unterstutzt/454>`_
- `System für kontinuierliche Audio-Aufzeichnung (BOB Projekt, Phase 1) <https://community.hiveeyes.org/t/system-fur-kontinuierliche-audio-aufzeichnung-bob-projekt-phase-1/728>`_


******************
State of the onion
******************
THIS IS A WORK IN PROGRESS. THERE MIGHT BE DRAGONS. YOU HAVE BEEN WARNED.

The software is based on GStreamer_ and the `GStreamer Python Bindings`_,
in turn using the fine PyGObject_ under the hood.

The software was tested successfully with Python 2.x, Python 3.x,
GStreamer 1.10.4 and GStreamer 1.14.4, on Linux and macOS.



*****
Setup
*****
This part of the documentation covers the installation of Saraswati.
The first step to using any software package is getting it properly installed.
Please read this section carefully.


Prepare environment
===================
Create the directory where Saraswati will store its files::

    mkdir /var/spool/saraswati

Synchronize system time with NTP, this is important for appropriate timestamping::

    timedatectl set-ntp true


Install prerequisites
=====================
As Saraswati is based on GStreamer_ and ALSA_,
let's install the relevant packages.


Clone source repository
-----------------------
::

    # Install git
    # {apt|brew} install git

    # Run clone process
    git clone https://github.com/hiveeyes/saraswati.git


Debian-based systems
--------------------
GStreamer::

    apt-get install gstreamer1.0 gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good

Python 3.x::

    apt-get install python3 python3-gst-1.0 python3-gi python3-tz

macOS systems
-------------
::

    brew install gstreamer gst-python gst-libav gst-plugins-base gst-plugins-good


*******
Running
*******
This part of the documentation covers the ways to run Saraswati.
Please read this section carefully.

Recording test audio
====================
There's already a basic implementation to

- ingest audio from GStreamer's ``audiotestsrc``,
- running it through ``flacenc`` to encode audio with
  the FLAC lossless audio encoder, and
- finally storing it using ``splitmuxsink``, a GStreamer component which
  multiplexes incoming streams into multiple time- or size-limited files

Each audio fragment will be timestamped with the current date/time
information in ISO-8601 format, using a qualified UTC offset of ``+0000``.

Invoke example program `flac-timestamp-chunked.py`_::

    python python/examples/flac-timestamp-chunked.py

Example output when being started at 03:35 CET::

    recording_2018-10-30T02:35:16+0000_0000.mka
    recording_2018-10-30T02:35:18+0000_0001.mka
    recording_2018-10-30T02:35:20+0000_0002.mka
    recording_2018-10-30T02:35:22+0000_0003.mka

Display segment metadata information embedded into the flile::

    mkvinfo '/var/spool/saraswati/recording_2018-10-30T05:48:48+0000_0000.mka' | grep Date
    | + Date: Tue Oct 30 05:48:48 2018 UTC


Recording real audio
====================
If you want to use a real audio source instead of the default
sine signal generated by ``audiotestsrc``, you will have to go
to the code to change this. However, this is pretty easy:

    In ``BasicPipeline.setup`` of `flac-timestamp-chunked.py`_,
    where the pipeline gets configured, please assign things like
    ``alsasrc device="hw:1"`` to the ``audio_input`` variable.



*******************
Project information
*******************

About
=====
The "Saraswati" program is released under the GNU AGPL license.
Its source code lives on `GitHub <https://github.com/hiveeyes/saraswati>`_ and
the Python package is published to `PyPI <https://pypi.org/project/saraswati/>`_.
You might also want to have a look at the `documentation <https://hiveeyes.org/docs/saraswati/>`_.

The software has been tested on Python 2.x and Python 3.x.

If you'd like to contribute you're most welcome!
Spend some time taking a look around, locate a bug, design issue or
spelling mistake and then send us a pull request or create an issue.

Thanks in advance for your efforts, we really appreciate any help or feedback.

Code license
============
Licensed under the GNU AGPL license. See LICENSE_ file for details.

.. _LICENSE: https://github.com/hiveeyes/saraswati/blob/master/LICENSE


----

Have fun!


.. _GStreamer: https://gstreamer.freedesktop.org/
.. _GStreamer Python Bindings: https://cgit.freedesktop.org/gstreamer/gst-python
.. _PyGObject: http://pygobject.readthedocs.io/
.. _ALSA: https://alsa-project.org/
.. _Single-board computer (SBC): https://en.wikipedia.org/wiki/Single-board_computer
.. _flac-timestamp-chunked.py: https://github.com/hiveeyes/saraswati/blob/master/python/examples/flac-timestamp-chunked.py
