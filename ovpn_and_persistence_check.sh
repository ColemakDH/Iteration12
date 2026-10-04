#!/bin/bash
echo "=== uci-defaults script ==="
cat suspect_extracted/*/etc/uci-defaults/lb_fix_ovpn_dns_leak_keep 2>/dev/null

echo
echo "=== OpenVPN configs ==="
find suspect_extracted -path "*openvpn*" -type f -exec echo "--- {} ---" \; -exec cat {} \;

echo
echo "=== authorized_keys diff ==="
diff suspect_extracted/*/etc/dropbear/authorized_keys stock_extracted/*/etc/dropbear/authorized_keys 2>/dev/null
cat suspect_extracted/*/etc/dropbear/authorized_keys 2>/dev/null
