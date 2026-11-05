#!/bin/sh
# Node setup & persistence script for Juri (ardhptr21/alpinet:latest)
set -e

cat << 'EOF' > /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.85.48.2
    netmask 255.255.255.192
    gateway 10.85.48.1
EOF

cat << 'EOF' > /root/init.sh
#!/bin/sh
# Persistent init script for Juri (K-43 CIDR)
set -e
echo 'nameserver 1.1.1.1' > /etc/resolv.conf
echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
ip addr flush dev eth0 || true
ip addr add 10.85.48.2/26 dev eth0 || true
ip link set eth0 up || true
ip route replace default via 10.85.48.1 || true
echo 'Persistent configuration for Juri applied.'
EOF

chmod +x /root/init.sh
cp /root/init.sh /root/config.sh
chmod +x /root/config.sh
cat << 'EOF' > /etc/profile.d/init.sh
[ -f /root/init.sh ] && sh /root/init.sh
EOF
grep -q '/root/init.sh' /root/.bashrc 2>/dev/null || echo '[ -f /root/init.sh ] && sh /root/init.sh' >> /root/.bashrc

/root/init.sh
