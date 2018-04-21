#########
saraswati
#########


*****
About
*****
saraswati is a robust, multi-channel audio recording, transmission and storage system.

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
and the independent research and development group Hiveeyes, see also:

- `hiverize.org - Vernetzt. Smart. Imkern. <https://hiverize.org/>`_
- `The Hiveeyes Project <https://hiveeyes.org/>`_
- `Bee Observer (BOB) - Uni Bremen und Hiveeyes werden als Citizen-Science-Projekte vom Forschungsministerium unterstützt <https://community.hiveeyes.org/t/bee-observer-bob-uni-bremen-und-hiveeyes-werden-als-citizen-science-projekte-vom-forschungsministerium-unterstutzt/454>`_
- `System für kontinuierliche Audio-Aufzeichnung (BOB Projekt, Phase 1) <https://community.hiveeyes.org/t/system-fur-kontinuierliche-audio-aufzeichnung-bob-projekt-phase-1/728>`_


******************
State of the onion
******************
THIS IS A WORK IN PROGRESS. THERE MIGHT BE DRAGONS.

The software is based on GStreamer_ and the `GStreamer Python Bindings`_,
in turn using the fine PyGObject_ under the hood.

We will start with basic ``gst-python`` examples and will gradually
improve the program to be production grade. We will definitively
have a look at OpenOB_.


*****
Setup
*****
Prerequisites::

    brew install gst-python gst-plugins-good
    virtualenv --python=python3 --system-site-packages .venv36


*******
Running
*******
::

    source .venv36/bin/activate
    python example.py


*******************
Project information
*******************

About
=====
The "saraswati" program is released under the GNU AGPL license.
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


.. _GStreamer: https://gstreamer.freedesktop.org/
.. _GStreamer Python Bindings: https://cgit.freedesktop.org/gstreamer/gst-python
.. _PyGObject: http://pygobject.readthedocs.io/
.. _OpenOB: https://jamesharrison.github.io/openob/
.. _Single-board computer (SBC): https://en.wikipedia.org/wiki/Single-board_computer
