#!/bin/sh
# Host setup & persistence script for Subnet A19 (Switch11): Chisa, Hodgeson
# Usage: sh <script>.sh [HostName]  (auto-detects hostname if omitted)
set -e

TARGET="${1:-$(hostname)}"
case "$TARGET" in
  Chisa|chisa)
    cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.1.194
    netmask 255.255.255.192
    gateway 10.85.1.193
EOF
    cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Chisa (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
ip addr flush dev eth0 || true
ip addr add 10.85.1.194/26 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.1.193 || true
echo 'Persistent configuration for Chisa applied.'
EOF
    ;;
  Hodgeson|hodgeson)
    cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.1.195
    netmask 255.255.255.192
    gateway 10.85.1.193
EOF
    cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Hodgeson (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
ip addr flush dev eth0 || true
ip addr add 10.85.1.195/26 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.1.193 || true
echo 'Persistent configuration for Hodgeson applied.'
EOF
    ;;
  *)
    echo "Usage: $0 {Chisa|Hodgeson}" >&2
    exit 1
    ;;
esac

chmod +x /root/init.sh
cp /root/init.sh /root/config.sh
chmod +x /root/config.sh
cat << 'EOF' > /etc/profile.d/init.sh
[ -f /root/init.sh ] && sh /root/init.sh
EOF
grep -q '/root/init.sh' /root/.bashrc 2>/dev/null || echo '[ -f /root/init.sh ] && sh /root/init.sh' >> /root/.bashrc
/root/init.sh
