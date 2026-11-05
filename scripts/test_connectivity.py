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

def api(endpoint):
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(f"{SERVER}/v3{endpoint}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

nodes = api(f"/projects/{PROJECT_ID}/nodes")
node_map = {n['name']: n for n in nodes}

def exec_cmd(node_name, cmd, wait=2.0):
    node = node_map.get(node_name)
    if not node or not node.get('console'):
        return f"Node {node_name} has no console"
    port = node['console']
    try:
        s = socket.socket()
        s.settimeout(wait + 2)
        s.connect(("10.4.89.247", port))
        time.sleep(0.3)
        s.sendall(b"\n")
        time.sleep(0.3)
        s.recv(2048)
        s.sendall(f"{cmd}\n".encode('utf-8'))
        time.sleep(wait)
        out = s.recv(8192).decode('utf-8', errors='ignore')
        s.close()
        return out
    except Exception as e:
        return f"Error connecting to {node_name}: {e}"

if __name__ == '__main__':
    targets = [
        ("Lain", "ip route"),
        ("Lain", "ping -c 2 10.85.0.65"),    # Shibuya (gateway)
        ("Lain", "ping -c 2 10.85.64.1"),     # Cyberia (core router)
        ("Lain", "ping -c 2 10.85.60.2"),     # Karl (far branch)
        ("Lain", "ping -c 2 8.8.8.8"),        # Internet via Cyberia NAT
        ("Karl", "ping -c 2 10.85.0.66"),     # Lain
        ("Karl", "ping -c 2 8.8.8.8"),        # Internet
        ("Masayuki", "ping -c 2 8.8.8.8"),    # Internet
        ("Alice", "ping -c 2 10.85.0.66"),    # Lain
        ("Alice", "ping -c 2 8.8.8.8"),       # Internet
    ]
    for node, cmd in targets:
        print(f"=== {node}: {cmd} ===")
        res = exec_cmd(node, cmd, wait=2.5)
        # print concise result
        for line in res.splitlines():
            if "bytes from" in line or "packet loss" in line or "default" in line or "unreachable" in line:
                print("  ", line)
        print()
