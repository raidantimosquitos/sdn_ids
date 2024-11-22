#!/bin/bash

# Print script commands and exit on errors.
#set -xe

apt-get update
apt-get upgrade
apt-get install -y --no-install-recommends git build-essential python3 python3-dev python3-venv mininet openvswitch-vswitch ant maven