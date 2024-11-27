# Setting up Zeek Virtual Machine

The following directory will provide a bash script to install Zeek software (`1-install-zeek.sh`) in the `zeek-vm`. The script must be run with `sudo` rights.

## Networking configuration
Please also run `2-set-up-private-bridge.sh` (again as `sudo`) to set up networking configuration with the private virtual bridge, this enables communication with the `mininet-vm`.

When completed, move on to [mininet-vm-setup](../mininet-vm-setup/README.md), when all VM setup is completed, you can move on to [zeek-scripts](../../zeek-scripts/README.md) directory on a brief introduction of the Zeek scripting language and its use in detection and prevention of cyber-threats.