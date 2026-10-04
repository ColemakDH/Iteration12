
## Setup (30 sec)
```bash
sudo apt update && sudo apt install -y binwalk squashfs-tools ent zstd
```

---

## PRIORITY 1: SSH Portal (closest to solved)

```bash
bash ssh_scratch_log.sh
```
Press `/`, test **one at a time**, write down full output each time:
{{printf "%#v" .}}
**Capture the ENTIRE output this time** — look for anything after "Vault:" that got cut off before.
{{printf "%v" .Vault}}

{{.Vault.Pin}}
{{.Vault.PIN}}
{{.Vault.Code}}


Stop the moment any of these returns a plain value instead of an error or pointer — that's your PIN. Flag: `tribectf{PIN}`.

---

## PRIORITY 2: OpenWrt netmgrd — trailing data check

If not already extracted:
```bash
binwalk -e openwrt-mt300n-v2-4.3.25-0318-1742298825.bin
mv _openwrt-mt300n-v2-4.3.25-0318-1742298825.bin.extracted suspect_extracted
```

```bash
bash netmgrd_elf_analysis.sh
```
Compare **file size** (top) against **last section's Offset+Size** (bottom). If file size is bigger, there's trailing data past the declared ELF content.

If so:
```bash
bash netmgrd_carve_trailing.sh <offset_from_last_section_end>
```

Also quickly run:
```bash
bash ovpn_and_persistence_check.sh
```
Read for a `remote` line (VPN server address) or injected SSH key.

---

## PRIORITY 3: Deadfish (only if time remains)

```bash
python3 deadfish_ry_atomic.py
```
Read all 6 permutations. If nothing printable:
```bash
python3 solve.py codex --deep
```

---

## Time discipline
- SSH: 10 min max — you're one field name away.
- OpenWrt: 10 min max — size comparison is instant, act on result immediately.
- Deadfish: whatever's left.

