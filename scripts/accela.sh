#!/bin/sh
# Node setup & persistence script for Accela (ardhptr21/alpinet:latest)
set -e

cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.32.2
    netmask 255.255.255.252
    gateway 10.85.32.1

auto eth1
iface eth1 inet static
    address 10.85.36.1
    netmask 255.255.252.0
EOF

cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Accela (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
sysctl -w net.ipv4.ip_forward=1
ip addr flush dev eth0 || true
ip addr add 10.85.32.2/30 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.32.1 || true
ip addr flush dev eth1 || true
ip addr add 10.85.36.1/22 dev eth1 || true
ip link set eth1 up || true
ip route replace default via 10.85.32.1 || true
echo 'Persistent configuration for Accela applied.'
EOF

chmod +x /root/init.sh
cp /root/init.sh /root/config.sh
chmod +x /root/config.sh
cat << 'EOF' > /etc/profile.d/init.sh
[ -f /root/init.sh ] && sh /root/init.sh
EOF
grep -q '/root/init.sh' /root/.bashrc 2>/dev/null || echo '[ -f /root/init.sh ] && sh /root/init.sh' >> /root/.bashrc

/root/init.sh
