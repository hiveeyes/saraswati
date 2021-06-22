import logging
import os
from typing import List

import click
import cloup
from cloup import Context

from saraswati import __appname__, __version__
from saraswati.model import Channel, SaraswatiSettings
from saraswati.recorder import SaraswatiRecorder
from saraswati.uploader import SaraswatiUploader
from saraswati.util import setup_logging

appname = f"{__appname__} {__version__}"

HELP_EPILOGUE = """
Examples:

    # Record a single channel from the built-in microphone.
    saraswati record --channel="testdrive source=autoaudiosrc"

    # Record a single channel and upload via rsync.
    saraswati record \\
        --channel="testdrive source=autoaudiosrc" \\
        --upload="rsync://foobar@daq.example.org:/var/spool/saraswati/testdrive/wp0Kel53aw/area-42/audionode-01"

    # Record two channels with different sine waves.
    saraswati record \\
        --channel="channel1 source=audiotestsrc wave=3 freq=200; foo=bar" \\
        --channel="channel2 source=audiotestsrc wave=3 freq=400"

    # Record to a specified location, using a different chunk duration.
    saraswati record \\
        --channel="testdrive source=autoaudiosrc" \\
        --chunk-duration=10 \\
        --spool=/var/spool/saraswati
    """


def validate_channel(ctx, param, value):
    """
    Parse multiple "--channel" command line options into list of Channel objects.
    """

    channels: List[Channel] = []
    for channel_raw in value:

        try:
            name, options_raw = channel_raw.split(" ", 1)
            options_list = options_raw.split(";")
            options_list = list(map(str.strip, options_list))
            options = {}
            for option_item in options_list:
                key, value = option_item.split("=", 1)
                options[key] = value.strip()

            source = options["source"]
            del options["source"]
            channel = Channel(name=name, source=source, options=options)
            channels.append(channel)
        except Exception as ex:
            raise click.BadParameter(
                f"\n--channel option needs to be in format "
                f"'channel1 source=audiotestsrc wave=3 freq=200; foo=bar'.\n\n"
                f"Exception: '{ex.__class__.__name__}: {ex}'\n"
                f"Offending value: '{channel_raw}'.\n"
            )

    return channels


channels_opt = click.option(
    "--channel",
    "-c",
    "channels",
    type=click.STRING,
    multiple=True,
    callback=validate_channel,
    help="Define channels to record, add multiple times to define more channels. "
    "The expression to define an audio source should be a GStreamer pipeline element syntax.",
)
spool_opt = click.option(
    "--spool",
    "spool_path",
    envvar="SPOOL_PATH",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    help="Absolute path to the spool directory",
)
upload_target_opt = click.option(
    "--upload",
    "-u",
    "upload_target",
    envvar="UPLOAD_TARGET",
    type=click.STRING,
    help="Define upload target. Currently, only rsync-based upload is implemented.",
)
upload_interval_opt = click.option(
    "--upload-interval",
    "upload_interval",
    envvar="UPLOAD_INTERVAL",
    type=click.INT,
    help="Pause between uploads (seconds)",
    default=5 * 60,
)
verbose_opt = click.option(
    "--verbose", envvar="VERBOSE", is_flag=True, help="Turn on verbose mode"
)


def print_version(ctx, param, value):
    """
    Implement "--version" flag globally.

    https://github.com/pallets/click/issues/1180#issuecomment-444815991
    """

    if not value or ctx.resilient_parsing:
        return

    print(appname)
    ctx.exit(0)


def print_help(ctx, param, value):
    """
    Augment "--help" flag.
    """

    if not value or ctx.resilient_parsing:
        return

    formatter = cloup.formatting.HelpFormatter(max_width=80)
    cli.format_help(ctx, formatter)
    print(formatter.getvalue())
    print(HELP_EPILOGUE)
    ctx.exit(0)


CONTEXT_SETTINGS = Context.settings(
    max_content_width=180,
    auto_envvar_prefix="SARASWATI",
)


@cloup.group(
    "saraswati", context_settings=CONTEXT_SETTINGS, invoke_without_command=True
)
@click.option(
    "--version",
    help="Print the package version and exit.",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=print_version,
)
@click.option(
    "--help",
    help="Print the package version and exit.",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=print_help,
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print_help(ctx, None, "--help")


@cli.command(
    "record", context_settings=Context.settings(auto_envvar_prefix="SARASWATI")
)
@channels_opt
@spool_opt
@click.option(
    "--chunk-duration",
    envvar="CHUNK_DURATION",
    type=click.INT,
    help="Duration of each chunk file (seconds)",
    default=5 * 60,
)
@click.option(
    "--chunk-max-files",
    envvar="CHUNK_MAX_FILES",
    type=click.INT,
    help="Maximum number of file fragments",
    default=9999,
)
@upload_target_opt
@upload_interval_opt
@verbose_opt
def record(
    channels: List[Channel],
    chunk_duration: int,
    chunk_max_files: int,
    spool_path: str,
    upload_target: str,
    upload_interval: int,
    verbose: bool,
):

    # Setup logging
    setup_logging(level=logging.DEBUG)

    # Add channels from environment variables.
    # TODO: Discuss priority / collision handling with channels from command line options.
    environment_channels = []
    for key in os.environ.keys():
        if key.startswith("SARASWATI_CHANNEL_"):
            environment_channels.append(os.environ[key])
    channels += validate_channel(None, None, environment_channels)

    # Create settings container.
    settings = SaraswatiSettings(
        channels=None,
        chunk_duration=chunk_duration,
        chunk_max_files=chunk_max_files,
        spool_path=spool_path,
        upload_target=upload_target,
        upload_interval=upload_interval,
    )

    # Ensure spool directory exists.
    settings.spool_path.mkdir(parents=True, exist_ok=True)

    # Create recorder.
    recorder = SaraswatiRecorder(settings=settings)

    # autoaudiosrc, osxaudiosrc, audiotestsrc wave=3 freq=200, alsasrc device="hw:1"

    # Add channels from both command line options and environment variables.
    for channel in channels:
        recorder.add_channel(name=channel.name, source=channel.source)

    # Invoke recording pipelines.
    recorder.start()
    recorder.record()

    # Create uploader.
    uploader = SaraswatiUploader(settings=settings)
    uploader.start()


@cli.command("setup")
@click.option("--systemd", is_flag=True, help="Install as systemd unit")
def setup(systemd: bool):
    if systemd:
        import saraswati.setup.systemd

        saraswati.setup.systemd.run()
    else:
        raise click.MissingParameter(message="Currently, only --systemd is implemented")
