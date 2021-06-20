#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Saraswati is a robust, multi-channel audio recording, transmission and storage system
# (c) 2018-2021 Andreas Motl <andreas@hiveeyes.org>
# (c) 2019 Diren Senger <diren@diren.de>
from functools import partial
from typing import List

import gi

from saraswati.model import Pipeline, SaraswatiSettings

gi.require_version("Gst", "1.0")

import logging
from datetime import datetime

import pytz
from gi.repository import GLib, Gst
from pkg_resources import parse_version

logger = logging.getLogger(__name__)


class SaraswatiRecorder:
    """
    This implements an audio encoding GStreamer pipeline in Python similar to this one::

        gst-launch-1.0 -e audiotestsrc ! flacenc ! flactag ! flacparse ! mux.audio_0 splitmuxsink muxer=matroskamux name=mux location="out_`date -u '+%Y-%m-%dT%H:%M:%S%z'`-%04d".mkv max-size-time=2500000000000

    See also:

    - https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html
    - https://gstreamer.freedesktop.org/documentation/multifile/splitmuxsink.html

    It is derived from these fine blueprints:

    - http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html

    """

    def __init__(self, settings: SaraswatiSettings):

        logger.info("Setting up audio recorder")

        self.settings = settings

        # The GLib main event loop object.
        self.mainloop = None

        # List for pipelines
        self.pipelines: List[Pipeline] = []

        # list for muxer
        self.muxer = []

        self.setup()
        self.print_status()

    def setup(self):
        # Setup PyGObject and GStreamer
        Gst.init(None)

        # Create main event loop object
        self.mainloop = GLib.MainLoop()

    @property
    def output_location(self):
        """
        Where to store the audio fragments.
        """
        return self.settings.spool_path / self.settings.spool_filename_pattern

    def print_status(self):
        logger.info(f"Spool location: {self.output_location}")
        logger.info(f"Chunk duration: {self.settings.chunk_duration} seconds")
        logger.info(
            f"Maximum number of file fragments: {self.settings.chunk_max_files}"
        )

    def add_channel(self, name: str, source: str):
        """
        :param name:   Channel name used for file names, etc., e.g. `channel1`
        :param source: GStreamer audio source definition, e.g. `alsasrc device="hw:1"`
        :return:
        """

        logger.info(f'Adding channel "{name}" on audio source "{source}"')

        # Configure audio pipeline

        # Configure duration of audio chunks in nanoseconds.
        chunk_duration_ns = self.settings.chunk_duration * (1000 ** 3)

        # Pipeline: Use FLAC encoder and Matroska container.
        # TODO: What about `muxer.audio_1`?
        pipeline_expression = (
            f"{source} ! audioconvert ! queue ! flacenc ! flactag ! flacparse ! "
            f"muxer.audio_0 splitmuxsink name=muxer muxer=matroskamux "
            f"max-size-time={chunk_duration_ns:.0f} max-files={self.settings.chunk_max_files}"
        )

        # TODO: Set `writing-app=saraswati` on `matroskamux`.
        # https://gstreamer.freedesktop.org/documentation/matroska/matroskamux.html?gi-language=c#matroskamux:writing-app

        pipeline_gst = Gst.parse_launch(pipeline_expression)

        # Launch pipeline
        pipeline = Pipeline(expression=pipeline_expression, gst=pipeline_gst)
        self.pipelines.append(pipeline)

        # Connect with bus
        bus = pipeline.gst.get_bus()
        bus.add_signal_watch()
        bus.connect("message", partial(self.on_message, pipeline))

        # Compute splitmuxsink timestamp name
        # http://gstreamer-devel.966125.n4.nabble.com/splitmuxsink-timestamp-name-for-python-td4688840.html
        current_muxer = pipeline.gst.get_by_name("muxer")
        if current_muxer:
            self.muxer.append(current_muxer)
            user_data = {"channel": name}

            # Dispatch name computation callback by GStreamer version
            signal_name = "format-location"
            signal_callback = self.on_format_location
            if parse_version(Gst.version_string()) >= parse_version("GStreamer 1.14.4"):
                logger.info("Detected GStreamer>=1.14.4, using 'format-location-full'")
                signal_name = "format-location-full"
                signal_callback = self.on_format_location_full

            current_muxer.connect(signal_name, signal_callback, user_data)

    # Running the shit
    def run(self):
        logger.info("Starting audio recorder")
        for i, pipeline in enumerate(self.pipelines):
            logger.info(f"Starting pipeline: {pipeline}")
            pipeline.gst.set_state(Gst.State.PLAYING)
        self.mainloop.run()

    # Bus message handler
    def on_message(self, pipeline: Pipeline, bus, message):

        structure = message.get_structure()
        if structure is None:
            return
        # logger.info('on_message: %s', structure.to_string())
        # logger.debug('tag: %s', message.parse_tag())

        # logger.debug('message:   %s\n%s', message, dir(message))
        # logger.debug('structure: %s\n%s', structure, dir(structure))
        # logger.debug('timestamp: %s', message.timestamp)

        # thing = self.pipeline.get_by_name('tagger')
        # logger.debug('thing: %s\n%s', thing, dir(thing))
        # logger.debug('tags: %s', thing.get_tag_list())
        # logger.debug('tags: %s', self.pipeline.get_tag_list())
        # logger.debug('muxer tags: %s', self.muxer.get_tag_list())

        if message.type == Gst.MessageType.EOS:
            logger.info("End of stream: {}".format(message))
            pipeline.gst.set_state(Gst.State.NULL)

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error("Pipeline error: {} ({})".format(err, debug))
            pipeline.gst.set_state(Gst.State.NULL)

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

        # logger.info('on_format_location')
        # print('tag:', splitmux.parse_tag())

        # Compute current timestamp (now) in ISO format, using UTC, with timezone offset
        # timestamp_format = '%Y-%m-%dT%H-%M-%S%z'
        timestamp_format = "%Y%m%dT%H%M%S%z"
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        # now = datetime.now().replace(tzinfo=pytz.timezone('Europe/Berlin'))
        timestamp = now.strftime(timestamp_format)

        # Use timestamp in Epoch format, with milliseconds for better accuracy
        # timestamp = time.time()
        # logger.info(datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))

        # Compute output location.
        location = str(self.output_location).format(
            timestamp=timestamp, fragment=fragment_id, channel=user_data["channel"]
        )
        logger.info(
            'Saving next audio fragment to "%s"',
            location.replace(str(self.settings.spool_path), "").strip("/"),
        )

        # logger.debug('splitmux: %s', splitmux)
        # logger.debug('fragment_id: %s', fragment_id)
        # logger.debug('first_sample: %s\n%s\n%s', first_sample, dir(first_sample), first_sample.get_info())
        # buffer = first_sample.get_buffer()

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


if __name__ == "__main__":

    # Setup logging
    from saraswati.util import setup_logging

    setup_logging(level=logging.DEBUG)

    # Run a basic pipeline test
    pm = SaraswatiRecorder()
    pm.add_channel(name="channel1", source='alsasrc device="hw:1"')
    pm.add_channel(name="channel2", source='alsasrc device="hw:2"')
    pm.add_channel(name="channel3", source='alsasrc device="hw:3"')
    pm.add_channel(name="channel4", source='alsasrc device="hw:4"')
    pm.run()
