#!/usr/bin/env python
# -*- coding: utf-8 -*-
# saraswati is a robust, multi-channel audio recording, transmission and storage system
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
import gi
gi.require_version('Gst', '1.0')

import sys
import pytz
import logging
from gi.repository import GObject, Gst
from datetime import datetime

logger = logging.getLogger(__name__)



class BasicPipeline:
    """
    This is the Python equivalent of::

        gst-launch-1.0 -e audiotestsrc ! flacenc ! flactag ! flacparse ! mux.audio_0 splitmuxsink muxer=matroskamux name=mux location="out_`date -u '+%Y-%m-%dT%H:%M:%S%z'`-%04d".mkv max-size-time=2500000000000

    See also:

    - https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html


    It is derived from these fine blueprints:

    - http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html

    """

    def __init__(self):

        logger.info('Starting PipelineTest')

        # Create main event loop object
        self.mainloop = GObject.MainLoop()

        # Where to store the audio fragments
        self.output_location = './var/spool/beehive_recording_{timestamp}_{fragment:04d}.mkv'

    def setup(self):

        logger.info('Configuring the pipeline')

        # Create pipeline object

        # Pure FLAC container
        pipeline_expression = \
            "audiotestsrc ! flacenc ! flactag ! flacparse ! " + \
            "muxer.audio_0 splitmuxsink name=muxer muxer=matroskamux max-size-time=1000000000000 max-files=10"

        # Ogg Vorbis container
        # https://xiph.org/flac/faq.html#general__native_vs_ogg
        #pipeline_expression = \
        #    "audiotestsrc ! progressreport ! vorbisenc name=encoder ! vorbistag name=tagger ! vorbisparse ! " + \
        #    "muxer.audio_0 splitmuxsink name=muxer muxer=matroskamux max-size-time=1000000000000 max-files=10"

        # souphttpclientsink
        # https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good/html/gst-plugins-good-plugins-souphttpclientsink.html
        """
        pipeline_expression = \
            "audiotestsrc ! progressreport ! vorbisenc name=encoder ! vorbistag name=tagger ! vorbisparse ! " + \
            "souphttpclientsink location=http://localhost:8080/filename.mkv"
        """

        pipeline_expression = \
            "audiotestsrc ! progressreport ! vorbisenc name=encoder ! vorbistag name=tagger ! vorbisparse ! " + \
            "muxer.audio_0 splitmuxsink name=muxer muxer=matroskamux sink=souphttpclientsink max-size-time=1000000000000 max-files=10 " + \
            "location=http://localhost:8080/filename.mkv"


        # souphttpclientsink location=http://server/filename.ogv
        # https://github.com/GStreamer/gst-plugins-good/blob/master/ext/soup/gstsouphttpclientsink.c

        logger.info(pipeline_expression)
        self.pipeline = Gst.parse_launch(pipeline_expression)

        # Connect with bus
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        # Compute splitmuxsink timestamp name
        # http://gstreamer-devel.966125.n4.nabble.com/splitmuxsink-timestamp-name-for-python-td4688840.html
        self.muxer = self.pipeline.get_by_name('muxer')
        if self.muxer:
            user_data = {'hello': 'bob'}
            self.muxer.connect("format-location-full", self.on_format_location, user_data)

    # Running the shit
    def run(self):
        logger.info('Running the pipeline')
        self.pipeline.set_state(Gst.State.PLAYING)
        self.mainloop.run()

    # Bus message handler
    def on_message(self, bus, message):

        structure = message.get_structure()
        if structure is None:
            return
        logger.info('on_message: %s', structure.to_string())
        #logger.debug('tag: %s', message.parse_tag())

        #logger.debug('message:   %s\n%s', message, dir(message))
        #logger.debug('structure: %s\n%s', structure, dir(structure))
        #logger.debug('timestamp: %s', message.timestamp)

        #thing = self.pipeline.get_by_name('tagger')
        #logger.debug('thing: %s\n%s', thing, dir(thing))
        #logger.debug('tags: %s', thing.get_tag_list())
        #logger.debug('tags: %s', self.pipeline.get_tag_list())
        #logger.debug('muxer tags: %s', self.muxer.get_tag_list())


        if message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            logger.info('End of stream: {}'.format(message))

        elif message.type == Gst.MessageType.ERROR:
            self.pipeline.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            logger.error('{}: {}'.format(err, debug))

    def on_format_location(self, splitmux, fragment_id, first_sample, user_data):
        """
        Callback for computing the output filename
        https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good/html/gst-plugins-good-plugins-splitmuxsink.html#GstSplitMuxSink-format-location-full

        splitmux:       The GstSplitMuxSink
        fragment_id:    The sequence number of the file to be created
        first_sample:   A GstSample containing the first buffer from the reference stream in the new file
        user_data:      User data set when the signal handler was connected
        """

        logger.info('on_format_location')
        #print('tag:', splitmux.parse_tag())

        # Compute current timestamp (now) in ISO format, using UTC, with timezone offset
        timestamp_format = '%Y-%m-%dT%H:%M:%S%z'
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        timestamp = now.strftime(timestamp_format)

        location = self.output_location.format(timestamp=timestamp, fragment=fragment_id)
        logger.info('Saving next audio fragment to "%s"', location)
        #logger.debug('splitmux: %s', splitmux)
        #logger.debug('fragment_id: %s', fragment_id)
        #logger.debug('first_sample: %s\n%s\n%s', first_sample, dir(first_sample), first_sample.get_info())
        #buffer = first_sample.get_buffer()

        # https://lazka.github.io/pgi-docs/Gst-1.0/classes/Buffer.html#Gst.Buffer.add_reference_timestamp_meta
        # https://lazka.github.io/pgi-docs/Gst-1.0/classes/ReferenceTimestampMeta.html
        # https://lazka.github.io/pgi-docs/Gst-1.0/classes/Caps.html#Gst.Caps
        """
        reference = Gst.Caps.from_string("timestamp/x-ntp")
        timestamp_epoch = int(now.strftime('%s'))
        duration = Gst.CLOCK_TIME_NONE
        buffer.add_reference_timestamp_meta(reference, timestamp_epoch, duration)
        """

        """
        logger.debug('buffer: %s\n%s', buffer, dir(buffer))
        #logger.debug('meta: %s', buffer.get_meta('a'))
        logger.debug('flags: %s', buffer.get_flags())
        #logger.debug('user_data: %s', user_data)
        logger.debug('reference timestamp: %s', buffer.get_reference_timestamp_meta())
        """

        return location


def setup_logging(level=logging.INFO):
    #log_format = '%(asctime)-15s [%(name)-10s] %(levelname)-7s: %(message)s'
    log_format = '%(asctime)-15s [%(name)s] %(levelname)-7s: %(message)s'
    logging.basicConfig(
        format=log_format,
        stream=sys.stderr,
        level=level)


if __name__ == '__main__':

    # Setup logging
    setup_logging(level=logging.DEBUG)

    # Setup PyGObject and GStreamer
    GObject.threads_init()
    Gst.init(None)

    # Run a basic pipeline test
    pipe = BasicPipeline()
    pipe.setup()
    pipe.run()
