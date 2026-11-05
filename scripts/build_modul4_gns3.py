import urllib.request, json, time, socket, sys

import os
SERVER = os.environ.get("GNS3_SERVER", "http://10.4.89.247:80")
USER = os.environ.get("GNS3_USER", "K-43")
PASS = os.environ["GNS3_PASS"]
PROJECT_ID = os.environ.get("GNS3_PROJECT_ID", "1cf3ee4e-17b2-45fd-94fb-3c39583e7299")

TMPL_ALPINET = "7f1d18f1-7f20-4fc2-a65b-b80fffb5253b"
TMPL_SWITCH  = "92a43283-9c7e-5a68-9695-1f05a2e8dd05"
TMPL_NAT     = "2d7eb722-90e8-56c1-8dfa-a30d79847984"

SYM_ROUTER = ":/symbols/affinity/square/red/router.svg"
SYM_SWITCH = ":/symbols/affinity/square/blue/switch.svg"
SYM_HOST   = ":/symbols/affinity/square/green/vm.svg"
SYM_NAT    = ":/symbols/affinity/square/blue/nat.svg"

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

print("[1] Connected and authenticated with GNS3 Controller.")

# 1. Clean existing nodes if any
existing_nodes = api(f"/projects/{PROJECT_ID}/nodes")
if existing_nodes:
    print(f"Cleaning {len(existing_nodes)} existing nodes...")
    for n in existing_nodes:
        try:
            api(f"/projects/{PROJECT_ID}/nodes/{n['node_id']}/stop", method="POST", data={})
        except:
            pass
        api(f"/projects/{PROJECT_ID}/nodes/{n['node_id']}", method="DELETE")
    time.sleep(2)

print("[2] Project clean. Defining nodes...")

# Define nodes with positions
# Center of canvas is Wired at (0, -100)
nodes_def = [
    # NAT
    ("NAT1", TMPL_NAT, SYM_NAT, 0, -450),

    # Routers
    ("Cyberia", TMPL_ALPINET, SYM_ROUTER, 0, -320),
    ("Wired", TMPL_ALPINET, SYM_ROUTER, 0, -100),
    ("Psyche", TMPL_ALPINET, SYM_ROUTER, -500, -250),
    ("Copland", TMPL_ALPINET, SYM_ROUTER, -500, -50),
    ("Schumann", TMPL_ALPINET, SYM_ROUTER, -300, 100),
    ("Accela", TMPL_ALPINET, SYM_ROUTER, -350, 260),
    ("Navi", TMPL_ALPINET, SYM_ROUTER, 400, -100),
    ("Tachibana", TMPL_ALPINET, SYM_ROUTER, 0, 80),
    ("Deus", TMPL_ALPINET, SYM_ROUTER, 180, 180),
    ("Protocol7", TMPL_ALPINET, SYM_ROUTER, 380, 240),
    ("Knights", TMPL_ALPINET, SYM_ROUTER, 620, 240),
    ("Phantoma", TMPL_ALPINET, SYM_ROUTER, 840, 180),
    ("Shibuya", TMPL_ALPINET, SYM_ROUTER, 840, 320),

    # Switches
    ("Switch1", TMPL_SWITCH, SYM_SWITCH, 220, -380),
    ("Switch2", TMPL_SWITCH, SYM_SWITCH, -280, -100),
    ("Switch3", TMPL_SWITCH, SYM_SWITCH, -700, -300),
    ("Switch4", TMPL_SWITCH, SYM_SWITCH, -700, -20),
    ("Switch5", TMPL_SWITCH, SYM_SWITCH, -550, 340),
    ("Switch6", TMPL_SWITCH, SYM_SWITCH, 650, -220),
    ("Switch7", TMPL_SWITCH, SYM_SWITCH, 650, -100),
    ("Switch8", TMPL_SWITCH, SYM_SWITCH, 480, 20),
    ("Switch9", TMPL_SWITCH, SYM_SWITCH, -160, 180),
    ("Switch10", TMPL_SWITCH, SYM_SWITCH, 100, 300),
    ("Switch11", TMPL_SWITCH, SYM_SWITCH, 380, 360),
    ("Switch12", TMPL_SWITCH, SYM_SWITCH, 980, 120),
    ("Switch13", TMPL_SWITCH, SYM_SWITCH, 950, 420),

    # Client Hosts
    ("JJ", TMPL_ALPINET, SYM_HOST, 340, -450),
    ("MyuMyu", TMPL_ALPINET, SYM_HOST, 340, -320),
    ("Karl", TMPL_ALPINET, SYM_HOST, -860, -380),
    ("Lin", TMPL_ALPINET, SYM_HOST, -860, -240),
    ("Juri", TMPL_ALPINET, SYM_HOST, -700, -140),
    ("Masayuki", TMPL_ALPINET, SYM_HOST, -860, -20),
    ("Akashic", TMPL_ALPINET, SYM_HOST, -480, 180),
    ("Omnipresence", TMPL_ALPINET, SYM_HOST, -720, 300),
    ("Denpa", TMPL_ALPINET, SYM_HOST, -700, 440),
    ("Alice", TMPL_ALPINET, SYM_HOST, 800, -280),
    ("Reika", TMPL_ALPINET, SYM_HOST, 800, -160),
    ("Taro", TMPL_ALPINET, SYM_HOST, 800, -80),
    ("Yasuo", TMPL_ALPINET, SYM_HOST, 400, 120),
    ("Miho", TMPL_ALPINET, SYM_HOST, 540, 140),
    ("Kuma", TMPL_ALPINET, SYM_HOST, 680, 120),
    ("Collective", TMPL_ALPINET, SYM_HOST, -240, 300),
    ("Ghost", TMPL_ALPINET, SYM_HOST, -80, 300),
    ("Lilith", TMPL_ALPINET, SYM_HOST, 20, 420),
    ("Specter", TMPL_ALPINET, SYM_HOST, 150, 420),
    ("Chisa", TMPL_ALPINET, SYM_HOST, 300, 480),
    ("Hodgeson", TMPL_ALPINET, SYM_HOST, 460, 480),
    ("Eiri", TMPL_ALPINET, SYM_HOST, 620, 360),
    ("Semi", TMPL_ALPINET, SYM_HOST, 1100, 60),
    ("Lain", TMPL_ALPINET, SYM_HOST, 880, 520),
    ("Mika", TMPL_ALPINET, SYM_HOST, 1020, 520),
]

created_nodes = {}
print(f"Creating {len(nodes_def)} nodes...")
for name, tmpl, sym, x, y in nodes_def:
    node = api(f"/projects/{PROJECT_ID}/templates/{tmpl}", method="POST", data={"x": x, "y": y})
    node_id = node["node_id"]
    # Rename and set symbol
    api(f"/projects/{PROJECT_ID}/nodes/{node_id}", method="PUT", data={"name": name, "symbol": sym})
    created_nodes[name] = node_id
    sys.stdout.write(f".")
    sys.stdout.flush()

print("\n[3] All nodes created. Creating links...")

# Define links: (Node1, adapter1, port1, Node2, adapter2, port2)
# For alpinet: eth0=(0,0), eth1=(1,0), eth2=(2,0), eth3=(3,0)
# For switch: Ethernet0..7 = (0,0)..(0,7)
# For NAT: nat0 = (0,0)
links_def = [
    # NAT1 to Cyberia
    ("NAT1", 0, 0, "Cyberia", 0, 0),

    # Cyberia Subnets
    ("Cyberia", 1, 0, "Switch1", 0, 0), # A1
    ("JJ", 0, 0, "Switch1", 0, 1),
    ("MyuMyu", 0, 0, "Switch1", 0, 2),
    ("Cyberia", 2, 0, "Wired", 0, 0),   # A2

    # Wired to Switch2, Navi, Tachibana
    ("Wired", 1, 0, "Switch2", 0, 0),   # A3
    ("Psyche", 0, 0, "Switch2", 0, 1),
    ("Copland", 0, 0, "Switch2", 0, 2),
    ("Schumann", 0, 0, "Switch2", 0, 3),

    # Psyche Subnet A4
    ("Psyche", 1, 0, "Switch3", 0, 0),
    ("Karl", 0, 0, "Switch3", 0, 1),
    ("Lin", 0, 0, "Switch3", 0, 2),

    # Copland Subnets A5, A6
    ("Copland", 1, 0, "Juri", 0, 0),     # A5 (direct)
    ("Copland", 2, 0, "Switch4", 0, 0),  # A6
    ("Masayuki", 0, 0, "Switch4", 0, 1),

    # Schumann Subnets A7, A8
    ("Schumann", 1, 0, "Akashic", 0, 0), # A7 (direct)
    ("Schumann", 2, 0, "Accela", 0, 0),  # A8 (link)

    # Accela Subnet A9
    ("Accela", 1, 0, "Switch5", 0, 0),
    ("Omnipresence", 0, 0, "Switch5", 0, 1),
    ("Denpa", 0, 0, "Switch5", 0, 2),

    # Wired to Navi A10
    ("Wired", 2, 0, "Navi", 0, 0),

    # Navi Subnets A11, A12, A13
    ("Navi", 1, 0, "Switch6", 0, 0),
    ("Alice", 0, 0, "Switch6", 0, 1),
    ("Reika", 0, 0, "Switch6", 0, 2),

    ("Navi", 2, 0, "Switch7", 0, 0),
    ("Taro", 0, 0, "Switch7", 0, 1),

    ("Navi", 3, 0, "Switch8", 0, 0),
    ("Yasuo", 0, 0, "Switch8", 0, 1),
    ("Miho", 0, 0, "Switch8", 0, 2),
    ("Kuma", 0, 0, "Switch8", 0, 3),

    # Wired to Tachibana A14
    ("Wired", 3, 0, "Tachibana", 0, 0),

    # Tachibana Subnet A15, A16
    ("Tachibana", 1, 0, "Switch9", 0, 0),
    ("Collective", 0, 0, "Switch9", 0, 1),
    ("Ghost", 0, 0, "Switch9", 0, 2),
    ("Tachibana", 2, 0, "Deus", 0, 0),   # A16

    # Deus Subnet A17, A18
    ("Deus", 1, 0, "Switch10", 0, 0),
    ("Lilith", 0, 0, "Switch10", 0, 1),
    ("Specter", 0, 0, "Switch10", 0, 2),
    ("Deus", 2, 0, "Protocol7", 0, 0),   # A18

    # Protocol7 Subnet A19, A20
    ("Protocol7", 1, 0, "Switch11", 0, 0),
    ("Chisa", 0, 0, "Switch11", 0, 1),
    ("Hodgeson", 0, 0, "Switch11", 0, 2),
    ("Protocol7", 2, 0, "Knights", 0, 0), # A20

    # Knights Subnet A21, A22
    ("Knights", 1, 0, "Eiri", 0, 0),     # A21 (direct)
    ("Knights", 2, 0, "Phantoma", 0, 0), # A22

    # Phantoma Subnet A23, A24
    ("Phantoma", 1, 0, "Switch12", 0, 0),
    ("Semi", 0, 0, "Switch12", 0, 1),
    ("Phantoma", 2, 0, "Shibuya", 0, 0), # A24

    # Shibuya Subnet A25
    ("Shibuya", 1, 0, "Switch13", 0, 0),
    ("Lain", 0, 0, "Switch13", 0, 1),
    ("Mika", 0, 0, "Switch13", 0, 2),
]

for n1, a1, p1, n2, a2, p2 in links_def:
    link_data = {
        "nodes": [
            {"node_id": created_nodes[n1], "adapter_number": a1, "port_number": p1},
            {"node_id": created_nodes[n2], "adapter_number": a2, "port_number": p2}
        ]
    }
    api(f"/projects/{PROJECT_ID}/links", method="POST", data=link_data)
    sys.stdout.write(".")
    sys.stdout.flush()

print(f"\n[4] All {len(links_def)} links created successfully!")
