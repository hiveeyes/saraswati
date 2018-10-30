#########
Saraswati
#########


*****
About
*****
Saraswati is a robust, multi-channel audio recording, transmission and storage system.

It is designed to run on `Single-board computer (SBC)`_
systems as well as larger machines.

It might become the designated work horse for flexible field recording
of audio signals in environmental monitoring systems.

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
and the people of the independent research and development project `Hiveeyes <https://hiveeyes.org/>`_, see also:

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

We will start with basic ``gst-python`` examples and will gradually
improve the program to be production grade. We will definitively
have a look at OpenOB_.


*****
Setup
*****

Prerequisites
=============
::

    brew install gstreamer gst-python libfft gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav


Setup
=====
::

    virtualenv --python=python3 --system-site-packages .venv36
    source .venv36/bin/activate

    pip install pytz

    export LDFLAGS="-L/usr/local/opt/libffi/lib"
    export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
    pip install pygobject



*******
Running
*******

There's already a basic implementation to

- ingest audio from GStreamer's `audiotestsrc`,
- running it through `flacenc` to encode audio with
  the FLAC lossless audio encoder, and
- finally storing it using `splitmuxsink`, a GStreamer component which
  multiplexes incoming streams into multiple time- or size-limited files

Each audio fragment will be timestamped with the current date/time
information in ISO-8601 format, using a qualified UTC offset of ``+0000``.

Invoke example program::

    source .venv36/bin/activate
    python python/examples/flac-timestamp-chunked.py

Example output::

    beehive_recording_2018-10-30T02:35:16+0000_0000.mkv
    beehive_recording_2018-10-30T02:35:18+0000_0001.mkv
    beehive_recording_2018-10-30T02:35:20+0000_0002.mkv
    beehive_recording_2018-10-30T02:35:22+0000_0003.mkv

Display segment metadata information embedded into the flile::

    mkvinfo 'var/spool/beehive_recording_2018-10-30T05:48:48+0000_0000.mkv' | grep Date
    | + Date: Tue Oct 30 05:48:48 2018 UTC


*******************
Project information
*******************

About
=====
The "Saraswati" program is released under the GNU AGPL license.
Its source code lives on `GitHub <https://github.com/hiveeyes/saraswati>`_ and
the Python package is published to `PyPI <https://pypi.org/project/saraswati/>`_.
You might also want to have a look at the `documentation <https://hiveeyes.org/docs/saraswati/>`_.

The software has been tested on Python 3.6.

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
.. _OpenOB: https://jamesharrison.github.io/openob/
.. _Single-board computer (SBC): https://en.wikipedia.org/wiki/Single-board_computer
