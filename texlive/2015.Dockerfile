FROM ubuntu:16.04

LABEL maintainer="Max Kuznetsov <maks.kuznetsov@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/mkuznets/latex-docker"

COPY setup-common.sh setup-latex.sh /tmp/

RUN \
    chmod +x /tmp/setup-common.sh && \
    /tmp/setup-common.sh && \
    rm /tmp/setup-common.sh

ENV DEBIAN_FRONTEND=noninteractive \
    LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8' \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 \
    TERM=xterm-color

RUN \
    chmod +x /tmp/setup-latex.sh && \
    /tmp/setup-latex.sh && \
    rm /tmp/setup-latex.sh
