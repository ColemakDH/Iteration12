#!/bin/bash
BIN=$(find suspect_extracted -path "*/usr/sbin/netmgrd" -type f | head -1)
echo "Target: $BIN"
echo

echo "=== file ==="
file "$BIN"

echo
echo "=== section headers ==="
readelf -S "$BIN"

echo
echo "=== actual file size vs last section end ==="
ls -la "$BIN"
echo "(compare file size above to last section's Offset+Size below)"
readelf -S "$BIN" | tail -8

echo
echo "=== IPs/domains in binary ==="
strings -n 6 "$BIN" | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}|https?://|\.(com|net|io|org)\b"

echo
echo "=== objdump headers (no arch flag - let it auto-detect) ==="
objdump -f "$BIN"
