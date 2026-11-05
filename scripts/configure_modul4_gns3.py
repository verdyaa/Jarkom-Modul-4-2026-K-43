import urllib.request, json, time, socket, sys

import os
SERVER = os.environ.get("GNS3_SERVER", "http://10.4.89.247:80")
USER = os.environ.get("GNS3_USER", "K-43")
PASS = os.environ["GNS3_PASS"]
PROJECT_ID = os.environ.get("GNS3_PROJECT_ID", "1cf3ee4e-17b2-45fd-94fb-3c39583e7299")

def get_token():
    data = f"username={USER}&password={PASS}".encode('utf-8')
    req = urllib.request.Request(f"{SERVER}/v3/access/users/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))['access_token']

token = get_token()

def api(endpoint, method="GET", data=None):
    global token
    headers = {"Authorization": f"Bearer {token}"}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{SERVER}/v3{endpoint}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            if content:
                return json.loads(content.decode('utf-8'))
            return None
    except urllib.error.HTTPError as e:
        if e.code == 401:
            token = get_token()
            headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(f"{SERVER}/v3{endpoint}", data=body, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp2:
                content = resp2.read()
                if content:
                    return json.loads(content.decode('utf-8'))
                return None
        raise e

def send_file(node_id, file_path, content):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}
    req = urllib.request.Request(f"{SERVER}/v3/projects/{PROJECT_ID}/nodes/{node_id}/files/{file_path}", data=content.encode('utf-8'), headers=headers, method="POST")
    urllib.request.urlopen(req)

# Get current nodes
nodes = api(f"/projects/{PROJECT_ID}/nodes")
node_map = {n['name']: n for n in nodes}
print(f"Loaded {len(node_map)} nodes from project.")

# Configurations dictionary:
# name: {
#   'interfaces': [ (iface, ip, netmask/prefix, gateway) ],
#   'is_router': bool,
#   'routes': [ (prefix, via) ],
#   'is_nat_gateway': bool
# }

configs = {
    # Routers
    "Cyberia": {
        "is_router": True,
        "is_nat_gateway": True,
        "interfaces": [
            ("eth0", "dhcp", "", ""),
            ("eth1", "10.85.64.1", "255.255.255.128", ""), # /25
            ("eth2", "10.85.64.129", "255.255.255.252", ""), # /30
        ],
        "routes": [
            ("10.85.0.0/18", "10.85.64.130") # All behind Wired
        ]
    },
    "Wired": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.64.130", "255.255.255.252", "10.85.64.129"),
            ("eth1", "10.85.56.1", "255.255.255.248", ""), # /29 (Switch2)
            ("eth2", "10.85.18.1", "255.255.255.252", ""), # /30 (Navi)
            ("eth3", "10.85.12.1", "255.255.255.252", ""), # /30 (Tachibana)
        ],
        "routes": [
            ("default", "10.85.64.129"),
            ("10.85.16.0/22", "10.85.18.2"), # Navi aggregate
            ("10.85.0.0/20", "10.85.12.2"),  # Tachibana aggregate
            ("10.85.60.0/22", "10.85.56.2"), # Psyche
            ("10.85.48.0/21", "10.85.56.3"), # Copland
            ("10.85.32.0/20", "10.85.56.4"), # Schumann & Accela
        ]
    },
    "Psyche": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.56.2", "255.255.255.248", "10.85.56.1"),
            ("eth1", "10.85.60.1", "255.255.252.0", ""), # /22
        ],
        "routes": [
            ("default", "10.85.56.1")
        ]
    },
    "Copland": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.56.3", "255.255.255.248", "10.85.56.1"),
            ("eth1", "10.85.48.1", "255.255.255.192", ""), # /26 (Juri)
            ("eth2", "10.85.50.1", "255.255.254.0", ""),   # /23 (Masayuki)
        ],
        "routes": [
            ("default", "10.85.56.1")
        ]
    },
    "Schumann": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.56.4", "255.255.255.248", "10.85.56.1"),
            ("eth1", "10.85.40.1", "255.255.255.248", ""), # /29 (Akashic)
            ("eth2", "10.85.32.1", "255.255.255.252", ""), # /30 (Accela)
        ],
        "routes": [
            ("default", "10.85.56.1"),
            ("10.85.36.0/22", "10.85.32.2") # Accela Subnet A9
        ]
    },
    "Accela": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.32.2", "255.255.255.252", "10.85.32.1"),
            ("eth1", "10.85.36.1", "255.255.252.0", ""), # /22
        ],
        "routes": [
            ("default", "10.85.32.1")
        ]
    },
    "Navi": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.18.2", "255.255.255.252", "10.85.18.1"),
            ("eth1", "10.85.16.1", "255.255.255.0", ""),   # /24 (Switch6)
            ("eth2", "10.85.17.1", "255.255.255.192", ""), # /26 (Switch7)
            ("eth3", "10.85.19.1", "255.255.255.0", ""),   # /24 (Switch8)
        ],
        "routes": [
            ("default", "10.85.18.1")
        ]
    },
    "Tachibana": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.12.2", "255.255.255.252", "10.85.12.1"),
            ("eth1", "10.85.14.1", "255.255.254.0", ""),   # /23 (Switch9)
            ("eth2", "10.85.8.1", "255.255.255.252", ""),  # /30 (Deus)
        ],
        "routes": [
            ("default", "10.85.12.1"),
            ("10.85.0.0/21", "10.85.8.2"),   # Deus downstream
            ("10.85.8.128/25", "10.85.8.2"), # Deus local
        ]
    },
    "Deus": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.8.2", "255.255.255.252", "10.85.8.1"),
            ("eth1", "10.85.8.129", "255.255.255.128", ""), # /25 (Switch10)
            ("eth2", "10.85.1.129", "255.255.255.252", ""), # /30 (Protocol7)
        ],
        "routes": [
            ("default", "10.85.8.1"),
            ("10.85.0.0/23", "10.85.1.130"), # Protocol7 downstream aggregate
        ]
    },
    "Protocol7": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.1.130", "255.255.255.252", "10.85.1.129"),
            ("eth1", "10.85.1.193", "255.255.255.192", ""), # /26 (Switch11)
            ("eth2", "10.85.1.1", "255.255.255.252", ""),   # /30 (Knights)
        ],
        "routes": [
            ("default", "10.85.1.129"),
            ("10.85.0.0/24", "10.85.1.2"), # Phantoma + Shibuya aggregate
            ("10.85.1.8/29", "10.85.1.2"), # Knights local
        ]
    },
    "Knights": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.1.2", "255.255.255.252", "10.85.1.1"),
            ("eth1", "10.85.1.9", "255.255.255.248", ""),   # /29 (Eiri)
            ("eth2", "10.85.0.129", "255.255.255.252", ""), # /30 (Phantoma)
        ],
        "routes": [
            ("default", "10.85.1.1"),
            ("10.85.0.0/24", "10.85.0.130"), # Phantoma + Shibuya aggregate
        ]
    },
    "Phantoma": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.0.130", "255.255.255.252", "10.85.0.129"),
            ("eth1", "10.85.0.161", "255.255.255.224", ""), # /27 (Switch12)
            ("eth2", "10.85.0.1", "255.255.255.252", ""),   # /30 (Shibuya)
        ],
        "routes": [
            ("default", "10.85.0.129"),
            ("10.85.0.64/26", "10.85.0.2"), # Shibuya
        ]
    },
    "Shibuya": {
        "is_router": True,
        "interfaces": [
            ("eth0", "10.85.0.2", "255.255.255.252", "10.85.0.1"),
            ("eth1", "10.85.0.65", "255.255.255.192", ""), # /26 (Switch13)
        ],
        "routes": [
            ("default", "10.85.0.1"),
        ]
    },

    # Client Hosts (25 hosts)
    "JJ": {"interfaces": [("eth0", "10.85.64.2", "255.255.255.128", "10.85.64.1")]},
    "MyuMyu": {"interfaces": [("eth0", "10.85.64.3", "255.255.255.128", "10.85.64.1")]},
    "Karl": {"interfaces": [("eth0", "10.85.60.2", "255.255.252.0", "10.85.60.1")]},
    "Lin": {"interfaces": [("eth0", "10.85.60.3", "255.255.252.0", "10.85.60.1")]},
    "Juri": {"interfaces": [("eth0", "10.85.48.2", "255.255.255.192", "10.85.48.1")]},
    "Masayuki": {"interfaces": [("eth0", "10.85.50.2", "255.255.254.0", "10.85.50.1")]},
    "Akashic": {"interfaces": [("eth0", "10.85.40.2", "255.255.255.248", "10.85.40.1")]},
    "Omnipresence": {"interfaces": [("eth0", "10.85.36.2", "255.255.252.0", "10.85.36.1")]},
    "Denpa": {"interfaces": [("eth0", "10.85.36.3", "255.255.252.0", "10.85.36.1")]},
    "Alice": {"interfaces": [("eth0", "10.85.16.2", "255.255.255.0", "10.85.16.1")]},
    "Reika": {"interfaces": [("eth0", "10.85.16.3", "255.255.255.0", "10.85.16.1")]},
    "Taro": {"interfaces": [("eth0", "10.85.17.2", "255.255.255.192", "10.85.17.1")]},
    "Yasuo": {"interfaces": [("eth0", "10.85.19.2", "255.255.255.0", "10.85.19.1")]},
    "Miho": {"interfaces": [("eth0", "10.85.19.3", "255.255.255.0", "10.85.19.1")]},
    "Kuma": {"interfaces": [("eth0", "10.85.19.4", "255.255.255.0", "10.85.19.1")]},
    "Collective": {"interfaces": [("eth0", "10.85.14.2", "255.255.254.0", "10.85.14.1")]},
    "Ghost": {"interfaces": [("eth0", "10.85.14.3", "255.255.254.0", "10.85.14.1")]},
    "Lilith": {"interfaces": [("eth0", "10.85.8.130", "255.255.255.128", "10.85.8.129")]},
    "Specter": {"interfaces": [("eth0", "10.85.8.131", "255.255.255.128", "10.85.8.129")]},
    "Chisa": {"interfaces": [("eth0", "10.85.1.194", "255.255.255.192", "10.85.1.193")]},
    "Hodgeson": {"interfaces": [("eth0", "10.85.1.195", "255.255.255.192", "10.85.1.193")]},
    "Eiri": {"interfaces": [("eth0", "10.85.1.10", "255.255.255.248", "10.85.1.9")]},
    "Semi": {"interfaces": [("eth0", "10.85.0.162", "255.255.255.224", "10.85.0.161")]},
    "Lain": {"interfaces": [("eth0", "10.85.0.66", "255.255.255.192", "10.85.0.65")]},
    "Mika": {"interfaces": [("eth0", "10.85.0.67", "255.255.255.192", "10.85.0.65")]},
}

print(f"Uploading /etc/network/interfaces and /root/config.sh to {len(configs)} nodes...")

for name, cfg in configs.items():
    if name not in node_map:
        print(f"Warning: {name} not found in nodes!")
        continue
    node_id = node_map[name]['node_id']

    # 1. Build /etc/network/interfaces
    ifaces_text = "auto lo\niface lo inet loopback\n\n"
    for iface, ip, mask, gw in cfg["interfaces"]:
        ifaces_text += f"auto {iface}\n"
        if ip == "dhcp":
            ifaces_text += f"iface {iface} inet dhcp\n\n"
        else:
            ifaces_text += f"iface {iface} inet static\n"
            ifaces_text += f"    address {ip}\n"
            ifaces_text += f"    netmask {mask}\n"
            if gw:
                ifaces_text += f"    gateway {gw}\n"
            ifaces_text += "\n"
    
    send_file(node_id, "etc/network/interfaces", ifaces_text)

    # 2. Build /root/config.sh
    sh_text = "#!/bin/sh\n# Setup script for " + name + "\nset -e\n\n"
    sh_text += "echo 'Nameserver 1.1.1.1' > /etc/resolv.conf\n"
    
    if cfg.get("is_router"):
        sh_text += "sysctl -w net.ipv4.ip_forward=1\n"
        if cfg.get("is_nat_gateway"):
            sh_text += "iptables -t nat -F || true\n"
            sh_text += "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE\n"

    # Add commands to ensure interfaces are up
    for iface, ip, mask, gw in cfg["interfaces"]:
        if ip == "dhcp":
            sh_text += f"udhcpc -i {iface} -b -p /var/run/udhcpc.{iface}.pid || true\n"
        else:
            sh_text += f"ip addr flush dev {iface} || true\n"
            # calculate prefix length from netmask
            prefix_len = sum(bin(int(x)).count('1') for x in mask.split('.'))
            sh_text += f"ip addr add {ip}/{prefix_len} dev {iface} || true\n"
            sh_text += f"ip link set {iface} up || true\n"
            if gw:
                sh_text += f"ip route replace default via {gw} || true\n"

    # Add routes
    for prefix, via in cfg.get("routes", []):
        if prefix == "default":
            sh_text += f"ip route replace default via {via} || true\n"
        else:
            sh_text += f"ip route replace {prefix} via {via} || true\n"

    sh_text += "\necho 'Configuration for " + name + " applied successfully!'\n"
    
    send_file(node_id, "root/config.sh", sh_text)
    sys.stdout.write(".")
    sys.stdout.flush()

print("\nFiles uploaded successfully! Starting all nodes...")

# Start all nodes
for n in nodes:
    try:
        api(f"/projects/{PROJECT_ID}/nodes/{n['node_id']}/start", method="POST", data={})
        sys.stdout.write("+")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error starting {n['name']}: {e}")

print("\nNodes started! Waiting 5 seconds for containers to initialize...")
time.sleep(5)

# Refresh node details to get console ports
nodes = api(f"/projects/{PROJECT_ID}/nodes")
node_map = {n['name']: n for n in nodes}

print("Executing /root/config.sh via console...")
def run_command(host, port, cmd):
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        time.sleep(0.3)
        s.sendall(b"\n")
        time.sleep(0.3)
        s.recv(2048)
        s.sendall(f"sh /root/config.sh\n".encode('utf-8'))
        time.sleep(0.8)
        out = s.recv(4096).decode('utf-8', errors='ignore')
        s.close()
        return out
    except Exception as e:
        return f"Error: {e}"

for name, cfg in configs.items():
    if name in node_map:
        cport = node_map[name].get('console')
        if cport:
            out = run_command("10.4.89.247", cport, "sh /root/config.sh")
            sys.stdout.write(".")
            sys.stdout.flush()

print("\nAll configurations executed successfully!")
