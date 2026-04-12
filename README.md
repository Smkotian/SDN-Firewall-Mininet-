### SDN-Based Firewall using POX Controller

A controller-based firewall using Software Defined Networking (SDN) principles to control traffic between hosts. The firewall should allow or block packets based on predefined rules (IP-based filtering) and demonstrate dynamic flow rule installation.


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

## 📁 Project Structure

```
sdn-firewall/
 ├── firewall.py
 ├── README.md
```

---

Project successfully demonstrates:

* Centralized traffic control using a controller
* Dynamic flow rule installation
* Effective filtering of network traffic

This project validates how SDN can be used to implement flexible and programmable network security policies.

---

