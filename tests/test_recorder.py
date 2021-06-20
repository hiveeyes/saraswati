import logging

from gi.overrides import Gst

from tests.util import load_module_from_file


def test_spike():

    spike = load_module_from_file("python/examples/flac-timestamp-chunked.py")

    # Setup logging
    spike.setup_logging(level=logging.DEBUG)

    # Setup PyGObject and GStreamer
    Gst.init(None)

    # Run a basic pipeline test
    pipe = spike.PipelineManager()
    pipe.add_pipe('audiotestsrc', "channel1")
    pipe.add_pipe('audiotestsrc', "channel2")
