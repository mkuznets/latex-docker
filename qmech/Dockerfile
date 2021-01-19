# Minimal texlive distribution
# to build github.com/mkuznets/quantum-mechanics-lectures

FROM ghcr.io/mkuznets/ubuntu:14.04-2020.11.04

LABEL maintainer="Max Kuznetsov <maks.kuznetsov@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/mkuznets/latex-docker"

RUN \
    apt-get update -qq && \
    apt-get install -f --yes --quiet --no-upgrade --no-install-recommends \
        texlive-latex-base \
        texlive-latex-recommended \
        texlive-latex-extra \
        cm-super-minimal \
        texlive-lang-cyrillic \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        latexmk \
        texlive-generic-recommended \
        latex-xcolor \
        pgf \
        make \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
