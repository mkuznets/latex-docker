#!/usr/bin/env bash

set -xe

export DEBIAN_FRONTEND=noninteractive

apt-get update -q
apt-get install --yes --quiet --no-upgrade --no-install-recommends \
  locales \
  tzdata

locale-gen --purge en_US.UTF-8

# ------------------------------------------------------------------------------
# Cleanup

apt-get clean
rm -rf /var/lib/apt/lists/*
