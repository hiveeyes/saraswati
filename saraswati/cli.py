import logging
from typing import List

import click
import cloup
from cloup import Context

from saraswati import __appname__, __version__
from saraswati.model import Channel, SaraswatiSettings
from saraswati.recorder import SaraswatiRecorder
from saraswati.util import setup_logging

appname = f"{__appname__} {__version__}"

HELP_EPILOGUE = """
Examples:

    # Record a single channel from the built-in microphone.
    saraswati record --channel="testdrive source=autoaudiosrc"

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
    help="Define channels to record. Add multiple times to define more channels",
)
spool_opt = click.option(
    "--spool",
    "spool_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    help="Absolute path to the spool directory",
)
debug_opt = click.option("--debug", is_flag=True, help="Turn on debug mode")


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

    formatter = cloup.formatting.HelpFormatter(max_width=120)
    cli.format_help(ctx, formatter)
    print(formatter.getvalue())
    print(HELP_EPILOGUE)
    ctx.exit(0)


CONTEXT_SETTINGS = Context.settings(
    max_content_width=180,
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


@cli.command("record")
@channels_opt
@spool_opt
@click.option(
    "--chunk-duration",
    type=click.INT,
    help="Duration of each chunk file (seconds)",
    default=60,
)
@click.option(
    "--chunk-max-files",
    type=click.INT,
    help="Maximum number of file fragments",
    default=9999,
)
@debug_opt
def record(
    channels: List[Channel],
    chunk_duration: int,
    chunk_max_files: int,
    spool_path: str,
    debug: bool,
):

    # Setup logging
    setup_logging(level=logging.DEBUG)

    # Create settings container.
    settings = SaraswatiSettings(
        channels=None,
        chunk_duration=chunk_duration,
        chunk_max_files=chunk_max_files,
        spool_path=spool_path,
    )

    # Ensure spool directory exists.
    settings.spool_path.mkdir(exist_ok=True)

    # Create recorder.
    recorder = SaraswatiRecorder(settings=settings)

    # autoaudiosrc, osxaudiosrc, audiotestsrc wave=3 freq=200, alsasrc device="hw:1"
    for channel in channels:
        recorder.add_channel(name=channel.name, source=channel.source)

    # Invoke recording pipelines.
    recorder.run()