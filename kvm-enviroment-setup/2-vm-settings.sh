#!/bin/bash

# Print script commands and exit on errors.
#set -xe

cp generate.php zeek-generate.php
mv generate.php mininet-generate.php

sed -i 's/template-debian-12/zeek-vm/g' zeek-generate.php 
sed -i 's/template-debian-12/mininet-vm/g' mininet-generate.php 
sed -i 's/cloud-init.cfg/zeek-cloud-init.cfg/g' zeek-generate.php 
sed -i 's/cloud-init.cfg/mininet-cloud-init.cfg/g' mininet-generate.php 

php zeek-generate.php
php mininet-generate.php
sudo cloud-localds zeek-cloud-init.iso zeek-cloud-init.cfg
sudo cloud-localds zeek-cloud-init.iso zeek-cloud-init.cfg