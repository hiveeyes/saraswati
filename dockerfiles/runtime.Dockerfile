# Docker build file for Saraswati runtime.
#
# Invoke like:
#
#   docker build --file=dockerfiles/runtime.Dockerfile --tag=saraswati-runtime .
#
FROM amd64/debian:bullseye-slim

RUN apt-get update && \
    apt-get install --yes \
        libgstreamer1.0 gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
        python3 python3-pip python3-gst-1.0 python3-gi python3-tz \
        alsa-utils mkvtoolnix flac wavpack

# Create /etc/saraswati
RUN mkdir -p /etc/saraswati

# Add user "saraswati"
RUN groupadd -r saraswati && useradd -r -g saraswati saraswati
RUN chown -R saraswati:saraswati /etc/saraswati

# Install saraswati
COPY . /src
RUN pip install /src

# Make process run as "saraswati" user
USER saraswati

# Invoke program
CMD saraswati
