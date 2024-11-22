from pox.core import core
from pox.lib.packet.ipv4 import ipv4
from pox.lib.addresses import IPAddr

log = core.getLogger()

# Store harmful IPs
harmful_ips = set()

def handle_notice_log(message):
    # Parse received logs
    if "Notice" in message:
        parts = message.split(": ")
        if len(parts) > 1:
            harmful_ips.add(IPAddr(parts[0]))
            log.info(f"Added {parts[0]} to harmful IPs list")

def launch():
    def start():
        core.openflow.addListenerByName("PacketIn", block_harmful_connections)
        log.info("Starting POX Controller")

        # Start listening for logs
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 6633))
        s.listen(5)

        def handle_connection(conn, addr):
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                handle_notice_log(data.decode('utf-8'))
            conn.close()

        import threading
        threading.Thread(target=lambda: handle_connection(*s.accept())).start()

    core.call_when_ready(start, "openflow")

def block_harmful_connections(event):
    ip_pkt = event.parsed.find(ipv4)
    if ip_pkt and ip_pkt.srcip in harmful_ips:
        log.info(f"Dropping packet from {ip_pkt.srcip}")
        event.connection.send(PacketIn.dummy(event.dpid, event.ofp, data=None))