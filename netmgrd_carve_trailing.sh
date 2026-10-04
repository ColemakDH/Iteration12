#!/bin/bash
# Usage: bash netmgrd_carve_trailing.sh <offset_where_sections_end>
BIN=$(find suspect_extracted -path "*/usr/sbin/netmgrd" -type f | head -1)
OFFSET="$1"
if [ -z "$OFFSET" ]; then
    echo "Usage: bash netmgrd_carve_trailing.sh <offset>"
    exit 1
fi
dd if="$BIN" of=trailing_blob.bin bs=1 skip="$OFFSET" 2>/dev/null
file trailing_blob.bin
xxd trailing_blob.bin | head -5
echo "Trying zstd decompress..."
zstd -d trailing_blob.bin -o trailing_decompressed 2>&1
cat trailing_decompressed 2>/dev/null
