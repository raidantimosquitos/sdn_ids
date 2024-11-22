# Setting up Mininet Virtual Machine

This directory introduces the software tools and set-up of the `mininet-vm`. The software installation script must be run as `sudo`. Some of the tools used in this machine are listed below, you are welcome to pursue further personalization, and even collaborate on our repository to further exploit all that these tools offer within this proposed enviroment:
- Mininet
- OpenVSwitch
- Pox controller

After all the tools have been installed, you should also clone the GitHub pox SDN controller repository to your mininet VM. As simple as running this command:
```bash
git clone https://github.com/noxrepo/pox.git
```

When completed, move on to [zeek-vm-setup](../zeek-vm-setup/README.md), when all VM setup is completed, you can move on to [pox-scripts](../../pox-scripts/README.md) directory to run the controller.