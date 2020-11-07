#!/usr/bin/env sh

set -e

TEXLIVE=$(apt-cache show texlive-base | grep Version | sed -r 's/.+([0-9]{4})\..+/\1/')
DISTRO=$(. /etc/os-release && echo "$ID")
DAY=$(TZ=Etc/UTC date '+%Y.%m.%d')

echo "${TEXLIVE}-${DISTRO}-${DAY}"
