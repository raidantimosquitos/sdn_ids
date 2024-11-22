# Running a Mininet network emulation with Python scripts

This section briefly describes what is the architecture we chose for the emulation, how to mirror the traffic from the network to the Zeek VM, and how to generate different types of traffic in the emulation.

## Network architecture

The major constraint we were facing is to mirror the traffic from the network to the Zeek IDS service running in `zeek-vm`, in order to do this our approach was to mirror all the traffic from the gateway (or outermost) switch. Thus we decided to implement a tree-like topology, because we can use the outermost (or root) switch in the topology to mirror all the traffic in its ports through the private virtual bridge to `zeek-vm`. The topology is illustrated in the below figure.

<img src="img/NetworkTopology.png" width="1000" align="center">

It is a relatively large topology for a test-bed framework, but we think it can be very versatile for further research specially in the case of Distributed Denial of Service Attacks (DDoS), and also mimicking real network behavior. For example where one (or some) host is attacking a server within the network, the rest of the hosts within the network would also try to communicate normally with the server. With this topology we can generate all kinds of traffic from the different sources and destinations and perform measurements such as: detection and mitigation time, round trip delay (RTT), false positive and false negative ratios, quality of service during an attack, etc.

## Step-by-step mininet emulation set-up

1. *Note:* This assumes that you have gone through the [pox-scripts section](../pox-scripts/README.md) and have a `mininet-vm` instance running the Pox controller.

2. Run the Python file `topology.py` in a new `mininet-vm` instance. The script generates a topology like the one illustrated earlier, the switch types are OpenVSwitch, they are OpenFlow SDN compatible switches and a key tool for traffic mirroring to the Zeek VM. This should prompt you the mininet CLI interface, someting like this:
```bash
res@mininet-vm:~$ sudo python3 topology/topology.py
mininet> 
```

3. Now you can test the ping reachability within the network, since the controller is running a forwarding L2 learning program, as explained in the [pox-scripts section](../pox-scripts/README.md), the switches will populate their switching tables based on the traffic it arrives. To test the reachability you can run `pingall` and should get an output like the one below:
```bash

```

4. So up to now we have a running emulation of the network where all the hosts can reach each other, but we still need this traffic to be mirrored to the `zeek-vm`, here is where the magic of OpenVSwitch comes to play. What we basically are going to do is configure the root switch `s1` in our case, to mirror all the traffic arriving to its ports that connect to the child switches (`s2`, `s3` and `s4`) to the private virtual bridge interface we configured earlier in the [kvm-environment-setup](../kvm-enviroment-setup/README.md) directory. 

5. First, open a new `mininet-vm` terminal instance, then we will have to add the VM interface (`enp7s0` in our case) as a port to the 0VS `s1`. To do this we run the following command:
```bash
# You can change the interface name and zeek-vm IP address according to what you have configured
res@mininet-vm:~$ sudo ovs-vsctl add-port s1 enp7s0 -- set interface enp7s0 type=gre options:remote_ip=192.168.100.2 
```

6. Second, configure `s1` to mirror the traffic from all its ports to `enp7s0` port.
```bash
# You can change the interface name to what you have configured
res@mininet-vm:~$ sudo ovs-vsctl -- set Bridge s1 mirrors=@m -- --id=@enp7s0 get Port enp7s0 -- --id=@m create Mirror name=zeekMirror select-all=true output-port=@enp7s0
```

7. Check that the traffic mirror object has been effectively created by running `sudo ovs-vsctl list Mirror`. You should see mirror `m0` binded to `enp7s0` port.

8. Now you are good to go, you can check that the traffic mirroring is working by opening a `zeek-vm` instance and running `sudo tcpdump -i enp7s0`.
```bash
res@zeek-vm:~$ sudo tcpdump -i enp7s0
```

9. `zeek-vm` is now listening on the private bridge interface, go the `mininet-vm` instance with mininet CLI (output of step 2 in this section). If you run `pingall` from the mininet CLI, you should see all the traffic appear in the `zeek-vm`.

## Conclusion

From here the networking configuration of the environment is ready, you can check section [zeek-scripts](../zeek-scripts/README.md) that will show you how Zeek IDS detects potentially threat events and it alerts the Pox controller, which in turn will have to install rules to drop the harmful traffic.


## TODO #1: Research on timestamps
In order to implement some of the evaluation metrics earlier discussed, we must set timestamps during different events within the emulation. This still remains to be done, I think I need to add to the `topology.py` script, the steps 5 and 6 in this guide, so that the bridging and mirroring is automatically configured and then we can trigger some traffic generation functions for certain amounts of time and record the timestamps. We thus avoid using the Mininet CLI.

## TODO #2: Traffic patterns

As for future implementations a more complete topology script could generate different traffic patters within different hosts (you can look at iperf mininet command for standard HTTP traffic), implement botnet simulators or other third-party tools that can be interesting to study.