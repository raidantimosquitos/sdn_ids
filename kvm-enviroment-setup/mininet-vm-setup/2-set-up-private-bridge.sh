#!/bin/bash

ip addr add 192.168.100.3 dev enp7s0
ip link set enp7s0 up
ip route add 192.168.100.2 dev enp7s0
iptables -A INPUT -p tcp --dport 6633 -j ACCEPT
sysctl -w net.ipv4.ip_forward=1