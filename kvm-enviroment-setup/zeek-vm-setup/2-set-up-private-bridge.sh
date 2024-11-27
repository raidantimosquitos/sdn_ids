#!/bin/bash

ip addr add 192.168.100.2 dev enp7s0
ip link set enp7s0 up
ip route add 192.168.100.3 dev enp7s0
iptables -t nat -A OUTPUT -o enp7s0 -s 127.0.0.1 -d 127.0.0.1 -p tcp --dport 6633 -j DNAT --to-destination 192.168.100.3:6633
sysctl -w net.ipv4.ip_forward=1
