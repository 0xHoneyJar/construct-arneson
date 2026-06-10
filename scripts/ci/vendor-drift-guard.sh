#!/usr/bin/env bash
# Vendor drift guard (arneson-with-gygax CI leg; R-1, sdd.md §3.4).
# Byte-diffs the vendored Gygax contract files against the real upstream checkout.
# Drift fails LOUDLY: the validators were written against the vendored bytes.
#
# Gygax root resolution: $ARNESON_GYGAX_ROOT, else ../construct-gygax sibling.

set -euo pipefail

VENDOR_DIR="domains/agent-systems/schemas/vendor"
GYGAX_ROOT="${ARNESON_GYGAX_ROOT:-../construct-gygax}"

if [ ! -d "$GYGAX_ROOT/schemas" ]; then
  echo "FAIL: no Gygax checkout at $GYGAX_ROOT (set ARNESON_GYGAX_ROOT or provide the sibling checkout)."
  echo "      The drift guard REQUIRES the real upstream — a stub cannot verify the pin."
  exit 1
fi

FAIL=0
for name in observed-trace.v1.schema.json observed-trace-batch.v1.md; do
  vendored="$VENDOR_DIR/$name"
  upstream="$GYGAX_ROOT/schemas/$name"
  if [ ! -f "$upstream" ]; then
    echo "FAIL: upstream contract file missing: $upstream"
    FAIL=1
    continue
  fi
  if cmp -s "$vendored" "$upstream"; then
    echo "OK: $name byte-identical to upstream"
  else
    echo "FAIL: CONTRACT DRIFT — $name differs from upstream at $GYGAX_ROOT."
    echo "      Re-vendor + update VENDOR.yaml + revisit validate_sidecar.py before producing batches."
    FAIL=1
  fi
done

# Self-pin check: vendored bytes still match VENDOR.yaml (same check the validators run).
python3 - <<'PYEOF'
import hashlib, re, sys
from pathlib import Path

vendor = Path("domains/agent-systems/schemas/vendor")
pin_text = (vendor / "VENDOR.yaml").read_text()
entries, current = {}, None
for line in pin_text.splitlines():
    m = re.match(r"\s*-?\s*vendored:\s*(\S+)", line)
    if m:
        current = Path(m.group(1)).name
        continue
    m = re.match(r"\s*sha256:\s*([0-9a-f]{64})", line)
    if m and current:
        entries[current] = m.group(1)
fail = 0
for name, pinned in entries.items():
    actual = hashlib.sha256((vendor / name).read_bytes()).hexdigest()
    if actual != pinned:
        print(f"FAIL: VENDOR.yaml pin stale for {name} (pinned {pinned[:12]}…, actual {actual[:12]}…)")
        fail = 1
    else:
        print(f"OK: VENDOR.yaml pin matches {name}")
sys.exit(fail)
PYEOF

[ "$FAIL" -eq 0 ] && echo "OK: vendored contract matches upstream + pin."
exit "$FAIL"
