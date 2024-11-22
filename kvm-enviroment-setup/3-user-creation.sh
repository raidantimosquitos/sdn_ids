#!/bin/bash

# login to each VM as debian/debian.

# once logged in inside each VM you must run the following script as sudo to create the res (research user)

# Print script commands and exit on errors.
set -xe

### create user res and give it sudo rights
sudo useradd -m -c "Research" res -s /bin/bash -p res
sudo bash -c 'echo "res:res" | chpasswd'
sudo bash -c 'echo "res ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/99_res'
sudo chmod 440 /etc/sudoers.d/99_res

#then logout and login by user res