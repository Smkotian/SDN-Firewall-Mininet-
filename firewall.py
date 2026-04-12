from pox.core import core
import pox.openflow.libopenflow_01 as of

# Initialize logger
log = core.getLogger()

# Dictionary to store MAC address to port mappings (learning switch behavior)
mac_to_port = {}


def _handle_ConnectionUp(event):
    """
    Triggered when a switch connects to the controller.
    """
    log.info("Switch connected: %s", event.connection)


def _handle_PacketIn(event):
    """
    Triggered when a packet arrives at the switch and no matching
    flow rule exists. The packet is sent to the controller.
    """
    packet = event.parsed

    # Ignore incomplete packets
    if not packet.parsed:
        return

    in_port = event.port

    # Learn the source MAC address and the port it came from
    mac_to_port[packet.src] = in_port

    # Extract IPv4 packet (if present)
    ip_packet = packet.find('ipv4')

    # ---------------- FIREWALL LOGIC ----------------
    if ip_packet:
        src_ip = str(ip_packet.srcip)
        dst_ip = str(ip_packet.dstip)

        # Block traffic from h1 (10.0.0.1) to h2 (10.0.0.2)
        if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
            log.info("BLOCKED: %s -> %s", src_ip, dst_ip)
            return  # Drop packet by not sending any action

        # Allow all other traffic
        log.info("ALLOWED: %s -> %s", src_ip, dst_ip)

    # ---------------- FORWARDING LOGIC ----------------
    # If destination MAC is known, forward to that port
    if packet.dst in mac_to_port:
        out_port = mac_to_port[packet.dst]
    else:
        # Otherwise, flood the packet to all ports
        out_port = of.OFPP_FLOOD

    actions = [of.ofp_action_output(port=out_port)]

    # ---------------- FLOW RULE INSTALLATION ----------------
    # Create a match structure based on packet fields
    match = of.ofp_match.from_packet(packet, in_port)

    # Create a flow modification message
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.actions = actions

    # Set timeouts for the flow rule
    msg.idle_timeout = 30   # Remove if idle for 30 seconds
    msg.hard_timeout = 60   # Remove after 60 seconds regardless

    # Send flow rule to the switch
    event.connection.send(msg)


def launch():
    """
    Entry point for POX controller module.
    Registers event handlers for switch connection and packet processing.
    """
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
