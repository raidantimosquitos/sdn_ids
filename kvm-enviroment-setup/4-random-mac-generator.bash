#!/bin/bash
# generate a random mac address
printf 'Zeek VM br-private MAC addres: 52:54:00:EF:%02X:%02X\n' $((RANDOM%256)) $((RANDOM%256))
printf 'Mininet VM br-private MAC address: 52:54:00:EF:%02X:%02X\n' $((RANDOM%256)) $((RANDOM%256))