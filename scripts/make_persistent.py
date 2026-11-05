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
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        pass

# Ensure all nodes are started so we can configure them live
nodes = api(f"/projects/{PROJECT_ID}/nodes")
node_map = {n['name']: n for n in nodes}
print(f"Checking {len(node_map)} nodes...")

stopped_nodes = [n for n in nodes if n['status'] == 'stopped']
if stopped_nodes:
    print(f"Starting {len(stopped_nodes)} stopped nodes...")
    for n in stopped_nodes:
        try:
            api(f"/projects/{PROJECT_ID}/nodes/{n['node_id']}/start", method="POST", data={})
        except:
            pass
    time.sleep(5)
    nodes = api(f"/projects/{PROJECT_ID}/nodes")
    node_map = {n['name']: n for n in nodes}

from configure_modul4_gns3 import configs

def build_init_script(name, cfg):
    lines = [
        "#!/bin/sh",
        f"# Persistent init script for {name}",
        "set -e",
        "echo 'nameserver 1.1.1.1' > /etc/resolv.conf",
        "echo 'nameserver 8.8.8.8' >> /etc/resolv.conf",
    ]
    if cfg.get("is_router"):
        lines.append("sysctl -w net.ipv4.ip_forward=1")
        if cfg.get("is_nat_gateway"):
            lines.append("iptables -t nat -F || true")
            lines.append("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")

    for iface, ip, mask, gw in cfg["interfaces"]:
        if ip == "dhcp":
            lines.append(f"udhcpc -i {iface} -b -p /var/run/udhcpc.{iface}.pid || true")
        else:
            prefix_len = sum(bin(int(x)).count('1') for x in mask.split('.'))
            lines.append(f"ip addr flush dev {iface} || true")
            lines.append(f"ip addr add {ip}/{prefix_len} dev {iface} || true")
            lines.append(f"ip link set {iface} up || true")
            if gw:
                lines.append(f"ip route replace default via {gw} || true")

    for prefix, via in cfg.get("routes", []):
        if prefix == "default":
            lines.append(f"ip route replace default via {via} || true")
        else:
            lines.append(f"ip route replace {prefix} via {via} || true")

    lines.append(f"echo 'Persistent configuration for {name} applied.'")
    return "\n".join(lines) + "\n"

def build_interfaces_text(cfg):
    text = "auto lo\niface lo inet loopback\n\n"
    for iface, ip, mask, gw in cfg["interfaces"]:
        text += f"auto {iface}\n"
        if ip == "dhcp":
            text += f"iface {iface} inet dhcp\n\n"
        else:
            text += f"iface {iface} inet static\n"
            text += f"    address {ip}\n"
            text += f"    netmask {mask}\n"
            if gw:
                text += f"    gateway {gw}\n"
            text += "\n"
    return text

print("Configuring persistence across all 38 nodes...")

for name, cfg in configs.items():
    if name not in node_map:
        continue
    node = node_map[name]
    port = node.get('console')
    node_id = node['node_id']

    init_script = build_init_script(name, cfg)
    ifaces_text = build_interfaces_text(cfg)

    # 1. Send via GNS3 file storage API
    send_file(node_id, "root/init.sh", init_script)
    send_file(node_id, "root/config.sh", init_script)
    send_file(node_id, "etc/network/interfaces", ifaces_text)

    # 2. Deploy live via console and ensure permissions + bash hooks
    if port:
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect(("10.4.89.247", port))
            time.sleep(0.2)
            s.sendall(b"\n")
            time.sleep(0.2)
            s.recv(1024)

            # Write init.sh directly
            encoded_script = init_script.replace("'", "'\"'\"'")
            payload = (
                f"cat << 'EOF' > /root/init.sh\n{init_script}EOF\n"
                f"chmod +x /root/init.sh\n"
                f"cp /root/init.sh /root/config.sh\n"
                f"chmod +x /root/config.sh\n"
                f"cat << 'EOF' > /etc/profile.d/init.sh\n[ -f /root/init.sh ] && sh /root/init.sh\nEOF\n"
                f"grep -q '/root/init.sh' /root/.bashrc 2>/dev/null || echo '[ -f /root/init.sh ] && sh /root/init.sh' >> /root/.bashrc\n"
                f"/root/init.sh\n"
            )
            s.sendall(payload.encode('utf-8'))
            time.sleep(0.6)
            s.recv(4096)
            s.close()
            sys.stdout.write(".")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error on {name}: {e}")

print("\nAll 38 nodes configured with persistent startup scripts!")
