FROM ubuntu:20.04

LABEL maintainer="Max Kuznetsov <maks.kuznetsov@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/mkuznets/latex-docker"

COPY setup.sh /tmp/

RUN \
    chmod +x /tmp/setup.sh && \
    /tmp/setup.sh && \
    rm /tmp/setup.sh
