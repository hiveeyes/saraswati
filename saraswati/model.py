from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from appdirs import user_data_dir


@dataclass
class Channel:
    name: str
    source: str
    options: Dict[str, str] = None


@dataclass
class SaraswatiSettings:

    # Channel definition.
    channels: List[Channel]

    # Chunking options.
    chunk_duration: Optional[int] = 5 * 60
    chunk_max_files: Optional[int] = 9999

    # Where to store the recordings.
    spool_path: Optional[str] = None
    spool_filename_pattern: Optional[
        str
    ] = "{year}/{month:02d}/{day:02d}/{channel}/{timestamp}_{channel}_{fragment:04d}.mka"

    # Where and how often to upload recordings.
    upload_target: Optional[str] = None
    upload_interval: Optional[int] = 5 * 60

    def __post_init__(self):
        if self.spool_path is not None:
            self.spool_path = Path(self.spool_path)
        else:
            from saraswati import __appname__

            self.spool_path = Path(user_data_dir(__appname__, "hiveeyes")) / "spool"


@dataclass
class Pipeline:
    expression: str
    gst: object = None
