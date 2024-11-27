import os

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
        self.addLink(root_switch, s2, intfName1='s1-s2', intfName2='s2-s1')
        self.addLink(root_switch, s3, intfName1='s1-s3', intfName2='s3-s1')
        self.addLink(root_switch, s4, intfName1='s1-s4', intfName2='s4-s1')


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
    CLI(net)
    net.stop()