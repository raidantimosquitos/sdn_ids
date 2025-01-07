# Automated Intrusion Detection System for Software Defined Networks

The following project implements an automated IDS based on [Zeek](https://zeek.org/) for ping-flooding attacks in an SDN environment. The emulation environment uses [Kernel-based Virtual Machines (KVMs)](https://linux-kvm.org/page/Main_Page), [Open vSwitch](https://www.openvswitch.org/), [Mininet](https://mininet.org/) and the [PoX SDN remote controller](https://github.com/noxrepo/pox).

It consists of two Virtual Machines, `mininet-vm` hosting the network emulation and `zeek-vm` hosting the IDS. All traffic in `mininet-vm` is mirrored to `zeek-vm` through a private virtual bridge. The structure of the repository is presented below:

```plaintext
Directory structure:
└── raidantimosquitos-sdn_ids/
    ├── README.md
    ├── kvm-enviroment-setup/
    │   ├── README.md
    │   ├── 1-vm-download.sh
    │   ├── 2-vm-settings.sh
    │   ├── 3-user-creation.sh
    │   ├── 4-random-mac-generator.bash
    │   ├── img/
    │   ├── mininet-vm-setup/
    │   │   ├── README.md
    │   │   ├── 1-install-mininet.sh
    │   │   └── 2-set-up-private-bridge.sh
    │   └── zeek-vm-setup/
    │       ├── README.md
    │       ├── 1-install-zeek.sh
    │       └── 2-set-up-private-bridge.sh
    ├── mininet-topology/
    │   ├── README.md
    │   ├── attack-sim.py
    │   ├── round_trip_time_study.xlsx
    │   ├── rtt_log.txt
    │   ├── topology.py
    │   └── img/
    ├── pox-scripts/
    │   ├── README.md
    │   └── pox-dos-handler.py
    ├── zeek-scripts/
    │   ├── README.md
    │   └── detect_icmp_dos_attack.zeek
    └── zeek_api/
        ├── README.md
        ├── call_api.py
        └── main.py
```

To set-up the environment, first you should go through directory `/kvm-environment-setup/`, this will:
- Create two Debian12 based VMs, `zeek-vm` and `mininet-vm`.
- Install the required packages on each VM.
- Set-up the infrastructure (private virtual bridge) for traffic mirroring between VMs.

Second, you can go through `zeek-scripts` and `pox-scripts` to set-up both the IDS service listening on the virtual bridge interface, and the controller script for reaction upon threat detection.

Finally you can go through `mininet-topology`, to setup the network topology and configure traffic mirroring.

Additionally, `zeek_api` approach is also introduced as a test on the implementation of REST API for controller and IDS communication.

