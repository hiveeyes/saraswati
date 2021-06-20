#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Saraswati is a robust, multi-channel audio recording, transmission and storage system
# (c) 2018-2021 Andreas Motl <andreas@hiveeyes.org>
import gi
gi.require_version('Gst', '1.0')

import sys
import pytz
import logging
from gi.repository import GLib, Gst
from datetime import datetime
import time
from pkg_resources import parse_version

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    This implements an audio encoding GStreamer pipeline in Python similar to this one::

        gst-launch-1.0 -e audiotestsrc ! flacenc ! flactag ! flacparse ! mux.audio_0 splitmuxsink muxer=matroskamux name=mux location="out_`date -u '+%Y-%m-%dT%H:%M:%S%z'`-%04d".mkv max-size-time=2500000000000

    See also:

    - https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html
    - https://gstreamer.freedesktop.org/documentation/multifile/splitmuxsink.html

    It is derived from these fine blueprints:

    - http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html

    """

    def __init__(self):

        logger.info('Starting audio recorder')

        # Create main event loop object
        self.mainloop = GLib.MainLoop()


        # list for pipelines
        self.pipelines = []

        # list for pipeline expression
        self.pipeline_expressions = []

        # list for muxer
        self.muxer = []


        # Where to store the audio fragments
        # TODO: Make configurable.
        self.output_location = './var/spool/recording_{channel}_{timestamp}_{fragment:04d}.mka'

    def add_pipe(self, audio_input, channel):
        """
        :param audio_input: audio input device, e.g. "alsasrc device="hw:1""
        :param channel: description of channel used for file names, e.g. "channel1"
        :return:
        """

        logger.info('Configuring the pipeline')

        # Configure audio pipeline

        # How long (ns) should the audio chunks be?
        # TODO: Make configurable.
        chunklength = 10 * (1000 ** 3)  # 10 seconds

        # Audio input source
        # TODO: Make configurable.
        #audio_input = 'audiotestsrc'
        #audio_input = 'alsasrc device="hw:1"'

        # Pipeline: Use FLAC encoder and Matroska container
        # TODO: Make "max-files" configurable.
        pipeline_expression = \
            "{audio_input} ! flacenc ! flactag ! flacparse ! " + \
            "muxer.audio_0 splitmuxsink name=muxer muxer=matroskamux max-size-time={chunklength:.0f} max-files=9999"

        self.pipeline_expressions.append(pipeline_expression.format(**locals()))



        # Launch pipeline
        self.pipelines.append(Gst.parse_launch(self.pipeline_expressions[-1]))

        # Connect with bus
        bus = self.pipelines[-1].get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        # Compute splitmuxsink timestamp name
        # http://gstreamer-devel.966125.n4.nabble.com/splitmuxsink-timestamp-name-for-python-td4688840.html
        current_muxer = self.pipelines[-1].get_by_name('muxer')
        if current_muxer:
            self.muxer.append(current_muxer)
            user_data = {'channel': channel}

            # Dispatch name computation callback by GStreamer version
            signal_name = "format-location"
            signal_callback = self.on_format_location
            if parse_version(Gst.version_string()) >= parse_version('GStreamer 1.14.4'):
                logger.info("Detected GStreamer>=1.14.4, using 'format-location-full'")
                signal_name = "format-location-full"
                signal_callback = self.on_format_location_full

            current_muxer.connect(signal_name, signal_callback, user_data)

    # Running the shit
    def run(self):
        for i, pipe in enumerate(self.pipelines):
            logger.info('Launching pipeline: %s', self.pipeline_expressions[i])
            pipe.set_state(Gst.State.PLAYING)
        self.mainloop.run()

    # Bus message handler
    def on_message(self, bus, message):

        structure = message.get_structure()
        if structure is None:
            return
        #logger.info('on_message: %s', structure.to_string())
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

    def on_format_location_full(self, splitmux, fragment_id, first_sample, user_data):
        return self.on_format_location(splitmux, fragment_id, user_data)

    def on_format_location(self, splitmux, fragment_id, user_data):
        """
        Callback for computing the output filename
        https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good/html/gst-plugins-good-plugins-splitmuxsink.html#GstSplitMuxSink-format-location-full

        splitmux:       The GstSplitMuxSink
        fragment_id:    The sequence number of the file to be created
        first_sample:   A GstSample containing the first buffer from the reference stream in the new file
        user_data:      User data set when the signal handler was connected
        """

        #logger.info('on_format_location')
        #print('tag:', splitmux.parse_tag())

        # Compute current timestamp (now) in ISO format, using UTC, with timezone offset
        #timestamp_format = '%Y-%m-%dT%H:%M:%S%z'
        #now = datetime.utcnow().replace(tzinfo=pytz.utc)
        #timestamp = now.strftime(timestamp_format)

        # timestamp in milliseconds for better accuracy
        timestamp = time.time()
        logger.info(datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))


        location = self.output_location.format(timestamp=timestamp, fragment=fragment_id, channel=user_data["channel"])
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
    log_format = '%(asctime)-15s [%(name)-15s] %(levelname)-7s: %(message)s'
    logging.basicConfig(
        format=log_format,
        stream=sys.stderr,
        level=level)


if __name__ == '__main__':

    # Setup logging
    setup_logging(level=logging.DEBUG)

    # Setup PyGObject and GStreamer
    Gst.init(None)

    # Run a basic pipeline test
    pm = PipelineManager()
    pm.add_pipe('alsasrc device="hw:1"', "channel1")
    pm.add_pipe('alsasrc device="hw:2"', "channel2")
    pm.add_pipe('alsasrc device="hw:3"', "channel3")
    pm.add_pipe('alsasrc device="hw:4"', "channel4")
    pm.run()
