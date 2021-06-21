# Docker build file for Saraswati development.
#
# Invoke like:
#
#   docker build --file=dockerfiles/develop.Dockerfile --tag=saraswati-develop .
#
FROM amd64/debian:bullseye-slim

RUN apt-get update && \
    apt-get install --yes \
        libgstreamer1.0 gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
        python3 python3-pip python3-gst-1.0 python3-gi python3-tz \
        alsa-utils mkvtoolnix flac wavpack
