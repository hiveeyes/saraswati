#!/usr/bin/env python
# -*- coding: utf-8 -*-
# saraswati is a robust, multi-channel audio recording, transmission and storage system
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
import sys
import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst


logger = logging.getLogger(__name__)


class BasicPipeline:
    """
    This is the Python equivalent of::

        gst-launch-1.0 audiotestsrc ! autoaudiosink

    See also:

    - https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html


    It is derived from these fine blueprints:

    - http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html

    """

    def __init__(self):

        logger.info('Starting PipelineTest')

        # Create main event loop object
        self.mainloop = GObject.MainLoop()

    def setup(self):

        logger.info('Configuring the pipeline')

        # Create pipeline object
        self.pipeline = Gst.parse_launch("audiotestsrc ! autoaudiosink")

        # Connect with bus
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    # Running the shit
    def run(self):
        logger.info('Running the pipeline')
        self.pipeline.set_state(Gst.State.PLAYING)
        self.mainloop.run()

    # Bus message handler
    def on_message(self, bus, message):

        logger.debug(message.get_structure())

        if message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            logger.info('End of stream: {}'.format(message))

        elif message.type == Gst.MessageType.ERROR:
            self.pipeline.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            logger.error('{}: {}'.format(err, debug))


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
