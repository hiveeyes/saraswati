import io
import logging
import shlex
import subprocess
import sys
import threading
import time

import teetime

from saraswati.model import SaraswatiSettings

logger = logging.getLogger(__name__)


class SaraswatiUploader(threading.Thread):

    # File with modification time lower than this duration will not be picked up (seconds).
    PICKUP_AGE_THRESHOLD = 25

    # Which network bandwidth to use when uploading (kB/second).
    BANDWIDTH_MAX = 80

    # Set network I/O timeout in seconds.
    IO_TIMEOUT = 15

    def __init__(self, settings: SaraswatiSettings):
        super().__init__()
        logger.info("Initializing uploader")
        self.settings = settings

    def start(self):

        if self.settings.upload_target is None:
            logger.info("No upload target, skipping uploader")
            return

        if not self.settings.upload_target.startswith("rsync://"):
            message = f"Unknown upload target protocol: {self.settings.upload_target}"
            logger.error(message)
            raise NotImplementedError(message)

        super().start()

    def run(self):
        logger.info("Starting uploader")
        while True:
            try:
                self.upload()
            except:
                logger.exception("Error while uploading")
            logger.info(
                f"The next upload will happen in {self.settings.upload_interval} seconds"
            )
            time.sleep(self.settings.upload_interval)

    def upload(self):
        logger.info("Uploading data")
        target = self.settings.upload_target
        if target.startswith("rsync://"):
            target = target.replace("rsync://", "")

            # Only use files which recently have not been written to.
            find = f"""
find "{self.settings.spool_path}"
    -type f
    -not -newermt "-{self.PICKUP_AGE_THRESHOLD} seconds"
    -printf "%P\\n"
            """.strip()

            # Command for uploading selected files.
            # TODO: Starting with `rsync 3.2.3` (6 Aug 2020), there will be the `--mkpath` option.
            # https://stackoverflow.com/a/65435579
            rsync = f"""
rsync 
    --archive --update --verbose 
    --remove-source-files --files-from=- 
    --bwlimit={self.BANDWIDTH_MAX} --timeout={self.IO_TIMEOUT} 
    "{self.settings.spool_path}" 
    "{target}"
            """.strip()

            # Reporting.
            logger.debug(f"Invoking command:\n{find}\n|\n{rsync}")

            # Run two commands, connected with pipes.
            finder = subprocess.Popen(shlex.split(find), stdout=subprocess.PIPE)
            finder.wait(timeout=20)

            # Run rsyncer
            # rsyncer = subprocess.Popen(shlex.split(rsync), stdin=finder.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Run rsyncer, with tee feature.
            buffer_stdout = io.BytesIO()
            buffer_stderr = io.BytesIO()
            rsyncer = teetime.popen_call(
                shlex.split(rsync),
                stdin=finder.stdout,
                stdout=(sys.stdout.buffer, buffer_stdout),
                stderr=(sys.stderr.buffer, buffer_stderr),
            )
            rsyncer.wait(timeout=300)

            if rsyncer.returncode == 0:
                logger.info("Upload succeeded")
            else:
                buffer_stderr.seek(0)
                stderr = buffer_stderr.read().decode()
                message = f"Rsync command failed: {stderr}"
                logger.error(message)
                raise ChildProcessError(message)

        else:
            message = f"Unknown upload target protocol: {self.settings.upload_target}"
            logger.error(message)
            raise NotImplementedError(message)
