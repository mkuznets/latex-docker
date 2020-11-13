FROM {{ base_image }}

LABEL maintainer="Max Kuznetsov <maks.kuznetsov@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/mkuznets/latex-docker"

COPY setup.sh /tmp/

RUN \
    chmod +x /tmp/setup.sh && \
    /tmp/setup.sh && \
    rm /tmp/setup.sh

RUN \
    groupadd --gid 2000 knuth && \
    useradd --gid 2000 --uid 2000 --create-home knuth
