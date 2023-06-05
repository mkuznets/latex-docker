#!/usr/bin/env bash

set -xe

INSTALL_FLAGS="-f --yes --quiet --no-upgrade --no-install-recommends"

apt-get update --quiet

# ------------------------------------------------------------------------------

PACKAGES=$(
  apt-cache depends texlive-full |
    grep Depends |
    cut -d ':' -f2 |
    grep -E -v -- '-doc$' |
    tr '\n' ' '
)

VERSION_ID=$(. /etc/os-release && echo "$VERSION_ID")

# shellcheck disable=SC2072
if [[ "$VERSION_ID" < "20.04" ]]; then
  PYGMENTS_PKG="python-pygments"
else
  PYGMENTS_PKG="python3-pygments"
fi

# ------------------------------------------------------------------------------

apt-get install $INSTALL_FLAGS \
  $PACKAGES \
  biber \
  gnuplot \
  imagemagick \
  $PYGMENTS_PKG

# ------------------------------------------------------------------------------
# Cleanup

apt-get clean
rm -rf /var/lib/apt/lists/*
