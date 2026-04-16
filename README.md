### SDN-Based Firewall using POX Controller

A controller-based firewall using Software Defined Networking (SDN) principles to control traffic between hosts. The firewall should allow or block packets based on predefined rules (IP-based filtering) and demonstrate dynamic flow rule installation.

## 📁 Project Structure

```
sdn-firewall/
 ├── firewall.py
 ├── README.md
```

## 🛠️ Setup & Requirements

### 🔹 Environment

* Ubuntu (VMware)
* Python (default system Python)
* Mininet
* POX Controller

### 🔹 Installation Steps

```bash
sudo apt update
sudo apt install mininet git -y

# Clone POX
git clone https://github.com/noxrepo/pox.git
cd pox
```

---

## ▶️ Execution Steps

### 1️⃣ Start POX Controller

```bash
cd ~/pox
./pox.py log.level --DEBUG openflow.of_01 firewall
```

---

### 2️⃣ Start Mininet (New Terminal)

```bash
sudo mn -c
sudo mn --topo single,3 --controller=remote --mac
```

---

### 3️⃣ Network Topology

* 1 Switch → `s1`
* 3 Hosts → `h1`, `h2`, `h3`
* IP Mapping:

  * h1 → 10.0.0.1
  * h2 → 10.0.0.2
  * h3 → 10.0.0.3

---

## 🔐 Firewall Logic

### Rule Implemented:

* ❌ Block: `10.0.0.1 → 10.0.0.2`
* ✅ Allow: All other traffic

### Working:

* Controller receives packets (PacketIn)
* Matches source & destination IP
* Applies:

  * Drop (no action) → blocked traffic
  * Forward → allowed traffic

---

## 🧪 Testing & Validation

### ✅ Test 1: Allowed Traffic

```bash
h1 ping h3
```

✔️ Result: Successful communication

---

### ❌ Test 2: Blocked Traffic

```bash
h1 ping h2
```

Result: Packet loss / no communication

---

### 📊 Performance Test 

```bash
h1 iperf -s &
h3 iperf -c h1
```

✔️ Allowed traffic shows throughput
❌ Blocked traffic fails to connect

---

### 📋 Flow Table Verification

```bash
sudo ovs-ofctl dump-flows s1
```

✔️ Shows dynamically installed flow rules

---

### 📜 Controller Logs

Example logs from POX:

```
ALLOWED: 10.0.0.1 -> 10.0.0.3
BLOCKED: 10.0.0.1 -> 10.0.0.2
```

✔️ Confirms firewall behavior

---

## 📊 Observations

* Flow rules are installed dynamically by controller
* PacketIn events trigger rule decisions
* Blocked traffic does not reach destination
* Allowed traffic results in flow rule creation
* Throughput differs between allowed and blocked flows

---

## 🧩 SDN Concepts Used

* Control Plane vs Data Plane separation
* OpenFlow protocol
* Flow rules (match + action)
* PacketIn / FlowMod messages

---
## 📌 Design Justification

This project implements an SDN-based firewall using a **single-switch topology with three hosts (h1, h2, h3)**. This design choice was intentional for the following reasons:

* **Simplicity & Clarity:** A single switch ensures that all traffic flows through one control point, making it easier to observe and demonstrate controller-based decision making.
* **Centralized Control Demonstration:** SDN principles emphasize separation of control and data planes. This topology clearly highlights how the controller governs all forwarding behavior.
* **Focused Firewall Behavior:** With minimal topology complexity, the firewall rule (blocking h1 → h2) can be isolated and validated without interference from routing or multi-hop behavior.

The **POX controller** was chosen due to its lightweight nature and ease of implementing OpenFlow-based logic using Python.

---

## 🔍 Flow Rule Design

The controller follows a **match–action paradigm**:

* **Match Fields:**

  * Source IP
  * Destination IP
  * MAC addresses (implicitly via `from_packet`)

* **Actions:**

  * **Drop (no action):** For blocked traffic (10.0.0.1 → 10.0.0.2)
  * **Forward:** For allowed traffic using learned MAC-to-port mapping

* **Timeouts:**

  * `idle_timeout = 30s` → Removes inactive flows
  * `hard_timeout = 60s` → Ensures periodic refresh of rules

This ensures efficient handling of repeated traffic while preventing stale rules.

---

## 📊 Performance Observation & Analysis

### 1. Latency (Ping)

* **Allowed Traffic (h1 → h3):**

  * Initial packets experience slight delay due to PacketIn → controller decision.
  * Subsequent packets are faster due to installed flow rules.

* **Blocked Traffic (h1 → h2):**

  * No response (100% packet loss)
  * Each packet triggers a PacketIn event (no flow rule installed for drop)

---

### 2. Throughput (iperf)

* **Allowed Traffic:**

  * Successful TCP connection established
  * Measurable throughput observed

* **Blocked Traffic:**

  * Connection fails
  * No throughput since packets are dropped

---

### 3. Flow Table Behavior

Using:

```bash
sudo ovs-ofctl dump-flows s1
```

* **Allowed flows:**

  * Entries are created dynamically
  * Packets are handled directly by the switch after rule installation

* **Blocked flows:**

  * No persistent flow rule (in current implementation)
  * Results in repeated controller involvement

---

## 🧪 Additional Validation

* Reverse traffic (h2 → h1) is allowed, confirming rule specificity
* Non-IP packets are forwarded normally (firewall applies only to IPv4)
* Learning switch behavior verified via MAC-to-port mapping

---

## ✅ Conclusion

This project successfully demonstrates:

* Controller–switch interaction using OpenFlow
* Dynamic flow rule installation
* Implementation of firewall policies using SDN
* Observable differences in behavior between allowed and blocked traffic

The results validate the effectiveness of SDN in enabling **programmable and centralized network security control**.



---

