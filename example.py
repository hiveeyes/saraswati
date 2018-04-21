#!/usr/bin/env python
# -*- coding: utf-8 -*-
# saraswati is a robust, multi-channel audio recording software based on GStreamer
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

        gst-launch-1.0 audiotestsrc ! alsasink
        gst-launch-1.0 audiotestsrc ! osxaudiosink

    It is derived from these fine blueprints:

    - http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html
    - https://www.jonobacon.com/2006/08/28/getting-started-with-gstreamer-with-python/

    - https://cgit.freedesktop.org/gstreamer/gst-python/tree/examples/helloworld.py
    - https://github.com/hadware/gstreamer-python-player/blob/master/player.py
    - https://github.com/brettviren/pygst-tutorial-org/blob/master/pipeline-example.py
    """

    def __init__(self):

        logger.info('Starting PipelineTest')

        # Create main event loop object
        self.mainloop = GObject.MainLoop()

        # Compute sink element based on platform
        # https://gstreamer.freedesktop.org/documentation/tutorials/basic/platform-specific-elements.html

        # Noop sink
        #self.sink_element = 'fakesink'

        # Speaker sink
        self.sink_element = 'alsasink'
        if sys.platform == 'darwin':
            self.sink_element = 'osxaudiosink'

    def setup(self):

        logger.info('Configuring the pipeline')

        # Create pipeline object
        self.pipeline = Gst.Pipeline.new("recorder")

        # Connect with bus
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        # Create audio source element
        self.audiotestsrc = Gst.ElementFactory.make("audiotestsrc", "audio")
        self.pipeline.add(self.audiotestsrc)

        # Create audio sink element
        self.sink = Gst.ElementFactory.make(self.sink_element, "sink")
        if self.sink is None:
            logger.error('Could not create sink element "{}"'.format(self.sink_element))
            sys.exit(1)
        self.pipeline.add(self.sink)

        # Link elements with each other
        self.audiotestsrc.link(self.sink)

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
