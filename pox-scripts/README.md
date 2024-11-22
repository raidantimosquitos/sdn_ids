# The Pox SDN controller

This section will instruct you how to run the Pox SDN controller in the `mininet-vm` of the KVM network emulation environment. It assumes that the [pox controller repository](https://github.com/noxrepo/pox) has been cloned in the main directory of the `mininet-vm`. According to the specification `pox` is designed to work with Python releases from 3.6 to 3.9, however we have run it with Python 3.11 in our machine without issues at the moment. If this can pose issues in your system, you should take a look at the [Python Virtual Environment configuration](https://virtualenv.pypa.io/en/latest/), to activate a virtual environment that uses older Python releases.

To test the functionality of the controller you can run in a `mininet-vm` terminal instance (in the pox repository directory) the following command:
```bash
./pox.py forwarding.l2_learning
```

This command will execute the `pox` controller with a simple L2 forwarding learning program that populates the tables in the switches of the network emulation based on learning from the packets L2 addresses of origin and target hosts.

Note that the `pox` remote controller is by default allocated in localhost address (`127.0.0.1`) with TCP socket port `6633`. To complete the verification of the simulation running, you can move to [mininet-topology](../mininet-topology/README.md) directory.

`TODO`: *Write a Python script for the Pox controller that implements L2 forwarding first, then remains listening for alerts from the Zeek IDS. Upon receiving an alert of potential harmful traffic, the controller should install rules on the switches of the network emulation to drop the traffic*. I included a ChatGPT generated script to have as reference.