#!/bin/sh
# Host setup & persistence script for Subnet A25 (Switch13): Lain, Mika
# Usage: sh <script>.sh [HostName]  (auto-detects hostname if omitted)
set -e

TARGET="${1:-$(hostname)}"
case "$TARGET" in
  Lain|lain)
    cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.0.66
    netmask 255.255.255.192
    gateway 10.85.0.65
EOF
    cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Lain (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
ip addr flush dev eth0 || true
ip addr add 10.85.0.66/26 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.0.65 || true
echo 'Persistent configuration for Lain applied.'
EOF
    ;;
  Mika|mika)
    cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.0.67
    netmask 255.255.255.192
    gateway 10.85.0.65
EOF
    cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Mika (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
ip addr flush dev eth0 || true
ip addr add 10.85.0.67/26 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.0.65 || true
echo 'Persistent configuration for Mika applied.'
EOF
    ;;
  *)
    echo "Usage: $0 {Lain|Mika}" >&2
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
