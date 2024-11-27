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

This will keep the zeek script listening on port the private virtual bridge port (where the mininet emulation traffic is mirrored to). If you go to your `mininet-vm` CLI instance and run a ping flooding command, such as `mininet> h1 ping -f h9`, you should start seeing how the detection mechanism of the script works. For now printing statements are added just to visualize and debug the behavior of the zeek script.

The current functionality is: upon detection the script will send a curl command to the address where the pox controller is located in the `mininet-vm`. The command contains a json-style structured HTTP message where the source and destination IPs, as well as the number of ICMP requests (pings) are included. You can see an example of the payload of the message and the curl command on the following code snippet:

```bash
controller_url = "http://192.168.100.3:6633"
payload = {"source_ip": "10.0.0.1", "destination_ip": "10.0.0.9", "request_count": 101}
curl -X POST -H 'Content-Type: application/json' -d payload controller_url
```

The implementation is considerably basic, but I know that Zeek has a framework named `Broker` that enables messaging from Zeek. I tried to implement it using Broker but did not succeed yet, but you can read a bit about it on this [link]().

*Possible `TODOS`*:
- *Implement Zeek Broker for more efficient messaging*
- *Maybe add further logic in the Zeek script to detect when ping-flooding finishes to inform controller again*
- *Include further data on payload of messages to integrate new functionalities*