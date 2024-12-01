import os
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

class TreeTopo(Topo):
    def build(self):
        # Root switch (s1)
        root_switch = self.addSwitch('s1')

        # Child switches (s2, s3, s4)
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Hosts connected to each child switch (3 hosts per switch)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        self.addLink(s2, h1)
        self.addLink(s2, h2)
        self.addLink(s2, h3)

        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        self.addLink(s3, h4)
        self.addLink(s3, h5)
        self.addLink(s3, h6)

        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        h9 = self.addHost('h9')
        self.addLink(s4, h7)
        self.addLink(s4, h8)
        self.addLink(s4, h9)

        # Link the root switch to child switches
        self.addLink(root_switch, s2, intfName1='s1-eth1', intfName2='s2-eth4')
        self.addLink(root_switch, s3, intfName1='s1-eth2', intfName2='s3-eth4')
        self.addLink(root_switch, s4, intfName1='s1-eth3', intfName2='s4-eth4')

def populate_switch_tables(net):
    """
    Perform a pingall to populate the switch flow tables.
    """
    print("Populating switch flow tables with pingall...")
    result = net.pingAll()
    if result == 0.0:
        print("Switch tables successfully populated (0% packet loss).")
    else:
        print(f"Switch tables populated with {result}% packet loss.")

if __name__ == '__main__':
    topo = TreeTopo()
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(
            name, ip='127.0.0.1', port=6653
        )
    )
    net.start()
    # Configure the root host s1 to mirror the traffic to zeek-vm
    os.system('sudo ovs-vsctl add-port s1 enp7s0 -- set interface enp7s0 type=gre options:remote_ip=192.168.100.2')
    os.system('sudo ovs-vsctl -- set Bridge s1 mirrors=@m -- --id=@enp7s0 get Port enp7s0 -- --id=@m create Mirror name=zeekMirror select-all=true output-port=@enp7s0')

    # Start RTT logging and flood attack simulation
    h1 = net.get('h1')
    h3 = net.get('h3')
    h9 = net.get('h9')

    # Populate switch tables
    populate_switch_tables(net)
    print("Sleep for 5 sec...")
    time.sleep(5)

    # Log RTTs for legitimate traffic
    log_file = "rtt_log.txt"
    with open(log_file, "w") as log:
        log.write("Phase, RTT (ms)\n")

    def log_rtts(phase, h1, h9, duration, interval=1.0):
        print(f"Starting logging for phase: {phase}")
        start_time = time.time()
        end_time = start_time + duration

        with open(log_file, "a") as log:
            while time.time() < end_time:
                rtt = h1.cmd(f"ping -c 1 {h9.IP()} | grep time= | awk -F'time=' '{{print $2}}' | awk '{{print $1}}'").strip()
                if rtt:
                    log.write(f"{phase}, {rtt}\n")
                time.sleep(interval)  # 1-second intervals

    def start_ping_flood(attacker, victim, duration):
        """
        Starts a ping flood from the attacker to the victim for the given duration.
        """
        print(f"Starting ping flood attack from {attacker.name} to {victim.IP()} for {duration} seconds")
        flood_cmd = f"timeout {duration} ping -f {victim.IP()} &"
        attacker.cmd(flood_cmd)

    # Simulate traffic phases
    try:
        print("Phase 1: Normal traffic (h1 -> h9)")
        log_rtts("before_attack", h1, h9, 15, interval=1.0)
        print("Sleep for 5 sec...")
        time.sleep(5)

        print("Phase 2: Flood attack starts (h3 -> h9)")
        ping_flood_duration = 15
        start_ping_flood(h3, h9, ping_flood_duration)
        log_rtts("during_attack", h1, h9, ping_flood_duration, interval=1.0)
        print("Sleep for 5 sec...")
        time.sleep(5)

        print("Phase 3: After mitigation (h1 -> h9)")
        log_rtts("after_mitigation", h1, h9, 15, interval=1)

    finally:
        print(f"RTT logs written to {log_file}")
        net.stop()
