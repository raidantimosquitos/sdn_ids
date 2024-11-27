#!/bin/bash

# Print script commands and exit on errors.
#set -xe

apt-get update
apt-get upgrade
apt-get install -y --no-install-recommends gpg
echo 'deb http://download.opensuse.org/repositories/security:/zeek/Debian_12/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list
curl -fsSL https://download.opensuse.org/repositories/security:zeek/Debian_12/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
apt-get update
apt-install zeek-6.0
echo 'export PATH=/opt/zeek/bin:$PATH' >> ~/.profile
source ~/.profile