from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
from pox.lib.util import dpid_to_str
from pox.lib.recoco import Task
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

log = core.getLogger()

# Function to block traffic from a specific IP
def block_ip(dpid, src_ip):
    connection = core.openflow.connections.get(dpid)
    if connection:
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match(dl_type=0x800, nw_src=IPAddr(src_ip))
        msg.actions = []  # Drop packets matching this rule
        connection.send(msg)
        log.info(f"Blocked IP {src_ip} on switch {dpid_to_str(dpid)}")
    else:
        log.warning(f"Switch {dpid_to_str(dpid)} not found or disconnected")

# Define the HTTP request handler
class ControllerRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read and parse the JSON payload
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            alert_data = json.loads(post_data)
            log.info(f"Received alert: {alert_data}")

            # Extract the IP to block (assumes alert_data contains "ip" key)
            ip_to_block = alert_data.get("source_ip")
            if ip_to_block:
                # Block the IP on all connected switches
                for dpid in core.openflow.connections.keys():
                    block_ip(dpid, ip_to_block)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Alert processed and IP blocked")
            else:
                log.warning("No 'ip' key found in alert data")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid alert data: 'ip' key required")
        except Exception as e:
            log.error(f"Failed to process alert: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal server error")


# Function to start the HTTP server
class HTTPServerWrapper:
    def __init__(self, port=6633):
        self.port = port
        self.server = HTTPServer(('0.0.0.0', port), ControllerRequestHandler)
        self.thread = None

    def start(self):
        log.info(f"HTTP server running at port {self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

class L2LearningSwitch:
    def __init__(self, connection, switch_name):
        self.connection = connection
        self.mac_to_port = {}
        self.switch_name = switch_name

        # Install event listeners
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        packet_in = event.ofp

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        # Learn the source MAC-to-port mapping
        self.mac_to_port[packet.src] = event.port

        # Log IP addresses if available
        src_ip = packet.find('ipv4').srcip if packet.find('ipv4') else "Unknown"
        dst_ip = packet.find('ipv4').dstip if packet.find('ipv4') else "Unknown"
        log.info(
            f"[{self.switch_name}] Packet from {src_ip} to {dst_ip} via port {event.port}"
        )

        # If the destination MAC is known, forward the packet
        if packet.dst in self.mac_to_port:
            port = self.mac_to_port[packet.dst]
            log.info(f"[{self.switch_name}] Forwarding to port {port}")
            self._send_packet(packet_in, port)
        else:
            # Flood the packet to all ports except the incoming port
            log.info(f"[{self.switch_name}] Flooding packet")
            self._send_packet(packet_in, of.OFPP_FLOOD)

    def _send_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

class L2Learning:
    def __init__(self):
        core.openflow.addListeners(self)
        self.http_server = HTTPServerWrapper(port=6633)
        self.switch_map = {}

    def _handle_ConnectionUp(self, event):
        switch_name = self._get_switch_name(event.dpid)
        log.info(f"Switch {switch_name} ({dpid_to_str(event.dpid)}) connected")
        self.switch_map[event.dpid] = switch_name
        L2LearningSwitch(event.connection, switch_name)

    def _get_switch_name(self, dpid):
        """
        Generate a human-readable switch name based on the dpid.
        Adjust this to match your Mininet topology.
        """
        dpid_str = dpid_to_str(dpid)
        if dpid_str.endswith("01"):
            return "s1"
        elif dpid_str.endswith("02"):
            return "s2"
        elif dpid_str.endswith("03"):
            return "s3"
        elif dpid_str.endswith("04"):
            return "s4"
        else:
            return f"Unknown Switch ({dpid_str})"

# POX launch function
def launch():
    """
    This function is called when the POX module is started.
    It initializes the L2 learning switch and starts the HTTP server.
    """
    log.info("Launching L2Learning module with HTTP server")
    l2_learning = L2Learning()
    core.registerNew(lambda: l2_learning)

    # Start the HTTP server in a separate thread
    l2_learning.http_server.start()
    log.info("L2Learning and HTTP server launched")
