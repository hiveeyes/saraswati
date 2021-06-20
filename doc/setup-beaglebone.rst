#################################
Running Saraswati on a BeagleBone
#################################

Contributed by Diren Senger. Thanks a stack!


*********
This Fork
*********

New in this fork is that the code works for four channels, the timestamp is more accurate and there is a script for server-transfer.
The original documentation can be found in the end of this document. I copied important pieces up here.

-- https://github.com/DieDiren/saraswati


*****************
Beagle-Bone setup
*****************

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


**********
User setup
**********

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


****************
First audio test
****************

::

    gst-launch-1.0 osxaudiosrc ! audioconvert ! level ! osxaudiosink

To test you audio hardware, you can run::

    arecord -l

	sudo arecord -D sysdefault:CARD=1 test1.wav &
	sudo arecord -D sysdefault:CARD=2 test2.wav &
	sudo arecord -D sysdefault:CARD=3 test3.wav &
	sudo arecord -D sysdefault:CARD=4 test4.wav


*********
GStreamer
*********

Don't forget to update before installing gstreamer::
	sudo apt-get update


GStreamer::

    apt install gstreamer1.0 gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good

Python 2.x::

    apt install python python-gst-1.0 python-gi python-tz

I also found instructions installing libgstreamer instead of gstreamer1.9, not sure if this makes a difference.


****************
Storage problems
****************

There isn't that much internal storage.
To list available storage::

	df -h

It should be just enough to use Saraswati.

Using the sd-card should not be the solution, but if you are getting troubles while testing, you can run::

	sudo /opt/scripts/tools/grow_partition.sh

This will expand your root partition to the sd-card.


***************
Using Saraswati
***************

I added pipes for four audio-devices::
	pm.add_pipe('alsasrc device="hw:1"', "channel1")
	pm.add_pipe('alsasrc device="hw:2"', "channel2")
	pm.add_pipe('alsasrc device="hw:3"', "channel3")
	pm.add_pipe('alsasrc device="hw:4"', "channel4")

I guess this will work on all beaglebones, but potentially you have to adjust the devices.

Create the directory saraswati uses::

	sudo mkdir /var/spool/saraswati/

To run Saraswati::

	sudo python python/examples/flac-timestamp-chunked.py


***************
Server transfer
***************

You need to set up a public-private key sign-up between the beaglebone and the server.

To run saraswati with transfer to some server, you first need to adjust automaticRsync.sh. Just add <port>, <path-to-key> and the <server-address>. Then run::

	sudo python python/examples/flac-timestamp-chunked.py & ./automaticRsync.sh

At the moment, the default in saraswati are 10-seconds chunks. The transfer to the server is initiated every 10 seconds. Files which are older than 25 seconds get deleted.

You might want to read the original instructions for saraswati in the end of this document.


*******
Outlook
*******

We need to solve the storage problems and can then also improve the rsync script.
It would be helpful to store the audio on the sd card in case the network connection breaks, but we want to avoid to many write cycles on the sd card.

We need to make sure that there is no drift between the channels. Maybe you can test this for us, e.g. using testaudio60.wav (bee sound with annoying noise in the beggining).

Other known issue: I did not update the error handling for four channels.
