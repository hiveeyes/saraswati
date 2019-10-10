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


*****
This Fork
*****

New in this fork is that the code works for four channels, the timestamp is more accurate and there is a script for server-transfer.
The original documentation can be found in the end of this document. I copied important pieces up here.


*****
Beagle-Bone setup
*****
I tested using the beaglebone black with 4 usb-soundcards.

Sofar, I used following image: bone-debian-9.5-lxqt-armhf-2018-10-07-4gb.img.xz

You can find it here: https://beagleboard.org/latest-images

Press the next to the sd-slot while plugging in the power source. For me, it took only some seconds and the image was copied.

If your beaglebone is connected via ethernet, you can reach it using::
	ssh debian@beaglebone.local

with the password::
	temppwd

It would make sense to use the version with out GUI for the next installation.

However, there seems to be a bug in the gstreamer package sources of the beaglebone debian 9.9 image.

I learned that a SD card can be used to flash one beaglebone only. After that, the sd-cart needs to be reformated.


*****
User setup
*****

For security, we need to create a new user (I called it leafcutter)::
	sudo passwd root 
	su -
	adduser leafcutter
	usermod -aG sudo leafcutter
	exit
	exit

Now log in with the new user and delete the default one::
	ssh leafcutter@beaglebone.local
	userdel -rf debian

*****
First audio test
*****

To test you audio hardware, you can run::
	arecord -l

	sudo arecord -D sysdefault:CARD=1 test1.wav & 
	sudo arecord -D sysdefault:CARD=2 test2.wav &
	sudo arecord -D sysdefault:CARD=3 test3.wav &
	sudo arecord -D sysdefault:CARD=4 test4.wav

*****
Gstreamer
*****

Don't forget to update before installing gstreamer::
	sudo apt-get update


GStreamer::

    apt install gstreamer1.0 gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good

Python 2.x::

    apt install python python-gst-1.0 python-gi python-tz

I also found instructions installing libgstreamer instead of gstreamer1.9, not sure if this makes a difference. 

****
Storage problems
****
There isn't that much internal storage.
To list available storage::
	df -h

It should be just enough to use saraswati.

Using the sd-card should not be the solution, but if you are getting troubles while testing, you can run::
	sudo /opt/scripts/tools/grow_partition.sh

This will expand your root partition to the sd-card.

*****
Using Saraswati
*****

I added pipes for four audio-devices::
	pm.add_pipe('alsasrc device="hw:1"', "channel1")
	pm.add_pipe('alsasrc device="hw:2"', "channel2")
	pm.add_pipe('alsasrc device="hw:3"', "channel3")
	pm.add_pipe('alsasrc device="hw:4"', "channel4")

I guess this will work on all beaglebones, but potentially you have to adjust the devices.

Create the directory saraswati uses::
	sudo mkdir /var/spool/saraswati/

To run saraswati::
	sudo python python/examples/flac-timestamp-chunked.py 

*****
Server transfer
*****
You need to set up a public-private key sign-up between the beaglebone and the server.

To run saraswati with transfer to some server, you first need to adjust automaticRsync.sh. Just add <port>, <path-to-key> and the <server-address>. Then run::

	sudo python python/examples/flac-timestamp-chunked.py & ./automaticRsync.sh

At the moment, the default in saraswati are 10-seconds chunks. The transfer to the server is initiated every 10 seconds. Files which are older than 25 seconds get deleted.

You might want to read the original instructions for saraswati in the end of this document.

*****
Outlook
*****

We need to solve the storage problems and can then also improve the rsync script.
It would be helpful to store the audio on the sd card in case the network connection breaks, but we want to avoid to many write cycles on the sd card.

We need to make sure that there is no drift between the channels. Maybe you can test this for us, e.g. using testaudio60.wav (bee sound with annoying noise in the beggining).

Other known issue: I did not update the error handling for four channels.

*************
Original documentation
*************


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
