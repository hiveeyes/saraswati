#################
Saraswati backlog
#################


******
Prio 1
******
- [o] Remove testaudio60.wav
- [o] What about ``muxer.audio_1``?
- [o] Record for a maximum number of seconds, using GStreamer's ``num-buffers=`` parameter on the source element
- [o] On Docker, ``Recording suspended: Disk space minimum threshold 10.0% reached`` is quickly reached
      To mitigate that, add an option ``--no-disk-usage-checks``.
- [o] Add upload option using FTP


******
Prio 2
******
- [o] Add option to upload to other storage systems. Maybe use ``fsspec`` to rule them all?
- [o] Add scheduling subsystem for controlling both recorder and uploader
- [o] Realtime statistics
- [o] Detect silence
- [o] PTH - inverted PTT
- [o] Signaling with MQTT
- [o] PTH from machine and browser
  - https://github.com/gdebat/Lossless-Audio-Streamer/blob/master/icecast-autostream.sh
  - https://community.hiveeyes.org/t/system-fur-kontinuierliche-audio-aufzeichnung-bob-projekt-phase-1/728/17
- [o] Add support for WavPack
  - https://community.hiveeyes.org/t/developing-saraswati-a-robust-multi-channel-audio-recording-transmission-and-storage-system/924/19
  - https://gstreamer.freedesktop.org/documentation/wavpack/wavpackenc.html
  - https://github.com/hiveeyes/saraswati/issues/7
- [o] Hardware device auto-discovery


****
Done
****
- [x] Make all parameters configurable
- [x] Add command line interface
- [x] Use default chunk size of 5 minutes
- [x] Upload files and purge from local disk
- [x] Run as system daemon by using a systemd unit file
- [x] Improve documentation re. disk storage
- [x] Document how to use a RAM disk for buffering
- [x] Document advanced SSH configuration (private key, port number) and write about
      "first-connect" acknowledgements.
      -- https://community.hiveeyes.org/t/developing-saraswati-a-robust-multi-channel-audio-recording-transmission-and-storage-system/924/30
- [x] Reflect the timestamp in folder names
      - https://community.hiveeyes.org/t/installation-von-saraswati-auf-einem-industrie-pc-mit-upload-auf-synology-nas/4048/18
