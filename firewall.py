from pox.core import core  # Import POX core module (main controller framework)

import pox.openflow.libopenflow_01 as of  # Import OpenFlow 1.0 library to communicate with switches


log = core.getLogger()  # Create a logger object to print messages in the POX console

mac_to_port = {}  
# Dictionary to store mapping: MAC address → switch port
# Used to implement learning switch behavior


def _handle_ConnectionUp(event):
    """
    Triggered when a switch connects to the controller.
    """
    log.info("Switch connected: %s", event.connection)  # Log that a switch has connected (event.connection = switch object)


def _handle_PacketIn(event):
    """
    Triggered when a packet arrives at the switch and no matching
    flow rule exists. The packet is sent to the controller.
    """

    packet = event.parsed # Extract the parsed packet object from the event

    # Ignore incomplete or malformed packets
    if not packet.parsed:
        return  

    in_port = event.port  # Get the port number on which the packet arrived at the switch

    mac_to_port[packet.src] = in_port   # Learn the source MAC address and map it to the incoming port
    # Example: "MAC A is reachable via port 1"

    ip_packet = packet.find('ipv4')   # Try to extract an IPv4 packet from the Ethernet frame


    # ---------------- FIREWALL LOGIC ----------------
    if ip_packet:  
        # Only apply firewall rules if it's an IP packet

        src_ip = str(ip_packet.srcip)  
        # Get source IP address as string

        dst_ip = str(ip_packet.dstip)  
        # Get destination IP address as string

        # Check firewall rule: block traffic from h1 to h2
        if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
            log.info("BLOCKED: %s -> %s", src_ip, dst_ip)  
            # Log that the packet is blocked

            return  
            # Drop packet by doing nothing (no forwarding, no rule installed)

        # If not blocked, allow traffic
        log.info("ALLOWED: %s -> %s", src_ip, dst_ip)  


    # ---------------- FORWARDING LOGIC ----------------

    # Check if destination MAC address is already known
    if packet.dst in mac_to_port:
        out_port = mac_to_port[packet.dst]  
        # Forward packet to the known port of destination

    else:
        out_port = of.OFPP_FLOOD  
        # If destination unknown → send to all ports (flood)


    actions = [of.ofp_action_output(port=out_port)]  
    # Define action: output packet to selected port


    # ---------------- FLOW RULE INSTALLATION ----------------

    # Create a match object based on packet fields (IP, MAC, ports, etc.)
    match = of.ofp_match.from_packet(packet, in_port)  
    # This defines what kind of packets this rule applies to

    # Create a flow modification message (FlowMod)
    msg = of.ofp_flow_mod()  
    # This message tells the switch to install a rule

    msg.match = match  
    # Set matching condition for the rule

    msg.actions = actions  
    # Set action (forwarding decision)


    # Set timeout values for the rule
    msg.idle_timeout = 30   
    # Remove rule if no packets match it for 30 seconds

    msg.hard_timeout = 60   
    # Remove rule after 60 seconds regardless of activity


    # Send the flow rule to the switch
    event.connection.send(msg)  
    # Switch will now handle similar packets without contacting controller


def launch():
    """
    Entry point for POX controller module.
    Registers event handlers for switch connection and packet processing.
    """

    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)  
    # Register handler for switch connection events

    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)  
    # Register handler for incoming packets (no matching rule)
