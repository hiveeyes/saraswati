import logging

from saraswati.model import SaraswatiSettings
from saraswati.uploader import SaraswatiUploader
from saraswati.util import setup_logging


def test_dryrun():

    # Setup logging.
    setup_logging(level=logging.DEBUG)

    # Create settings container.
    settings = SaraswatiSettings(
        channels=None, upload_target="rsync://foobar@daq.example.org:/tmp/testdrive"
    )

    # Create uploader.
    uploader = SaraswatiUploader(settings=settings)

    # Run a basic test.
    # uploader.upload()
