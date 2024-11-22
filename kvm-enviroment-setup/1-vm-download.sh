#!/bin/bash

# Print script commands and exit on errors.
#set -xe

###########################################################################################
# create the outer machine in either way below (by a cloud image or by a netinstall image, 
# or from a cloud service like OpenStack):
###########################################################################################

#1. by using a cloud image:
# refer to https://blog.programster.org/create-debian-12-kvm-guest-from-cloud-image

grep LIBVIRT_DEFAULT_URI ~/.bashrc > /dev/null
if [[ $? != 0  ]]; then
       echo export LIBVIRT_DEFAULT_URI=\'qemu:///system\' >> ~/.bashrc
fi
source ~/.bashrc
sudo apt update

sudo apt install --no-install-recommends -y qemu-system libvirt-clients libvirt-daemon-system virt-manager qemu-util

sudo apt install -y cloud-utils whois php-cli php-yaml 

wget https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2

cp debian-12-generic-amd64.qcow2 zeek-debian-12.qcow2
mv debian-12-generic-amd64.qcow2 mininet-debian-12.qcow2


DESIRED_SIZE=40G

sudo qemu-img resize zeek-debian-12.qcow2 $DESIRED_SIZE
sudo qemu-img resize mininet-debian-12.qcow2 $DESIRED_SIZE

wget https://files.programster.org/tutorials/cloud-init/create-debian-12-kvm-guest-from-cloud-image/generate.php

# Before moving to the next step: 
# Correct the sshPublicKeys in that .php file (you can refer to the programster tutorial) 