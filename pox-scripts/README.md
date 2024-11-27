# The Pox SDN controller

This section will instruct you how to run the Pox SDN controller in the `mininet-vm` of the KVM network emulation environment. It assumes that the [pox controller repository](https://github.com/noxrepo/pox) has been cloned in the main directory of the `mininet-vm`. According to the specification `pox` is designed to work with Python releases from 3.6 to 3.9, however we have run it with Python 3.11 in our machine without issues at the moment. If this can pose issues in your system, you should take a look at the [Python Virtual Environment configuration](https://virtualenv.pypa.io/en/latest/), to activate a virtual environment that uses older Python releases.

The script provided in this repository is named `pox_http_l2.py`. It consists of two main threads:
- OpenFlow thread (*on port 6653*) for the management of the OpenVSwitch switches running in the mininet emulation. It basically implemenents L2 forwarding on all switches of the topology, and can implement connection blocking.
- HTTP server thread (*on port 6633*) for actively listening to requests from Zeek IDS running on `zeek-vm`.

This script must be located in the `pox/pox/ext/` directory of the cloned repository of the pox controller. To run the script, you can run in a `mininet-vm` terminal instance (in the pox repository directory) the following command, it is important to specify the port 6653 for the OpenFlow protocol communications, otherwise it will conflict with the HTTP server listening on port 6633:
```bash
./pox.py openflow.of_01 --port=6653 ext.pox_http_l2
```

This command will execute the `pox` controller with two threads:
- A first thread that implements a L2 forwarding learning program that populates the tables in the switches of the network emulation based on learning from the packets L2 addresses of origin and target hosts. This thread also can calls function `block_ip()` to block IPv4 addresses based on the Zeek IDS logic.
- A second thread that starts an HTTP server and remains listening for messages from the Zeek IDS in `zeek-vm`. To complete the verification of the simulation running, you can move to [mininet-topology](../mininet-topology/README.md) directory.

`TODO`: *Maybe add further functionality to the Python script, some ideas:*
- *Unblock IP address upon certain amount of time without suspicious behaviour, detection logic also to be applied on Zeek IDS*.
- *Isolation of a whole subnet (hosts steming from one of the child switches). IP address assignment to be modified in this case on topology.py script*.