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
for name in observed-trace.v1.schema.json observed-trace-batch.v1.md signal-taxonomy.v1.schema.json; do
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

# Source↔vendor convergence guard (sprint-2, G-5): Arneson AUTHORS the 9 signal
# values; Gygax publishes the canonical copy we vendor. This is the only check
# that makes vendoring-a-list-we-authored load-bearing — it fails LOUDLY if the
# source enum (session-events-base.schema.yaml) and the published taxonomy ever
# drift apart in value set OR canonical order.
python3 - <<'PYEOF'
import json, re, sys
from pathlib import Path

vendor = Path("domains/agent-systems/schemas/vendor")
tax = json.loads((vendor / "signal-taxonomy.v1.schema.json").read_text())
vendored_enum = tax["$defs"]["signalClassification"]["enum"]

src_path = Path("schemas/core/session-events-base.schema.yaml")
src = src_path.read_text().splitlines()

# Locate the top-level `signal:` event block (2-space indent), then the single
# `values: [...]` it contains (signal.classification). Other event blocks also
# carry `values:`, so we MUST scope to this block, not grep the whole file.
start = next((i for i, ln in enumerate(src) if re.match(r"^  signal:\s*$", ln)), None)
if start is None:
    print(f"FAIL: convergence guard could not locate the `signal:` block in {src_path}")
    sys.exit(1)
end = next((j for j in range(start + 1, len(src)) if re.match(r"^  \S", src[j])), len(src))
vals = None
for ln in src[start:end]:
    m = re.search(r"values:\s*\[([^\]]*)\]", ln)
    if m:
        vals = [v.strip() for v in m.group(1).split(",") if v.strip()]
        break
if vals is None:
    print(f"FAIL: convergence guard found no `values: [...]` under signal.classification in {src_path}")
    sys.exit(1)

if vals == vendored_enum:
    print(f"OK: source signal.classification enum == vendored signal-taxonomy ({len(vals)} values, canonical order)")
    sys.exit(0)
print("FAIL: SOURCE↔VENDOR DIVERGENCE — signal taxonomy drift (set or order).")
print(f"      source   (session-events-base.schema.yaml): {vals}")
print(f"      vendored (signal-taxonomy.v1.schema.json):  {vendored_enum}")
print("      Re-vendor from gygax OR reconcile the source enum — the two must match exactly.")
sys.exit(1)
PYEOF

[ "$FAIL" -eq 0 ] && echo "OK: vendored contract matches upstream + pin + source convergence."
exit "$FAIL"
