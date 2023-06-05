FROM ubuntu:20.04

LABEL maintainer="Max Kuznetsov <maks.kuznetsov@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/mkuznets/latex-docker"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8' \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 \
    TERM=xterm-color

COPY setup.sh /tmp/

RUN \
    chmod +x /tmp/setup.sh && \
    /tmp/setup.sh && \
    rm /tmp/setup.sh
