import logging

from saraswati.model import SaraswatiSettings
from saraswati.recorder import SaraswatiRecorder
from saraswati.util import setup_logging


def test_spike():

    # Setup logging.
    setup_logging(level=logging.DEBUG)

    # Create settings container.
    settings = SaraswatiSettings(channels=None)

    # Create recorder.
    recorder = SaraswatiRecorder(settings=settings)

    # Run a basic pipeline test.
    recorder.add_channel(name="channel1", source='audiotestsrc')
    recorder.add_channel(name="channel2", source='audiotestsrc')
