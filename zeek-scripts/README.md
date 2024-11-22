# Zeek: an open source Network security monitoring tool

Zeek will act as a real-time Intrusion Detection System in our enviroment. We want to configure it to analyze real-time mirrored traffic and in the event of detecting a potential threat, it must message the remote Pox controller about its findings.

The Zeek software is complex and offers a lot of different functionality. So far we have implemented a couple of scripts only to detect ping-flooding or ICMP DoS attacks. They are based on two different principles, described below:
- Ping counting in an observation window: basically this script triggers Zeek alert in the case of receiving more than *x* ICMP packets in a set observation time window of *T* seconds. If more than *x* ICMP packets are received within *T* seconds, Zeek will write the Notice logs with the IP address of the source of this ping flooding.
- The second principle is by counting the number of ICMP packets per connection, and informing the controller to apply the logic.

You can explore all that Zeek scripting offers in [their guides and documentation](https://docs.zeek.org/en/current/scripting/index.html).

## Launching Zeek script on a specific interface

To launch a zeek script on a particular interface you should run the following command:

```bash
res@zeek-vm:~$ zeek -i enp7s0 detect_icmp_dos_attack.zeek
```

This will keep the zeek script listening on port the private virtual bridge port (where the mininet emulation traffic is mirrored to). If you go to your `mininet-vm` CLI instance and run a ping flooding command, such as `mininet> h1 ping -f h9`, you should start seeing how the detection mechanism of the script works. For now printing statements are added just to visualize and debug the zeek script. Still `TODO` is the communication between the detection of such events and the remote pox controller in `mininet-vm`.