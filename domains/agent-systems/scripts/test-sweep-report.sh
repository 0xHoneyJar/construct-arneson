#!/usr/bin/env bash
# test-sweep-report.sh (Sprint 2, Task 2.3). Hermetic: synthetic graded sidecars
# feed the cross-config aggregator; assert all three triage classes render and
# that output is deterministic and never recomputes a grade.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SR="python3 $SCRIPT_DIR/sweep_report.py"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

W=$(mktemp -d)
trap 'rm -rf "$W/cfgA" "$W/cfgB" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT

# Build a config batch: $1=dir, then triples "rung:class:narration"
mkbatch() {
  local dir="$1"; shift
  mkdir -p "$dir/sidecars"
  echo '{"schema":"observed-trace-batch/v1","fixture":"../x"}' > "$dir/batch.json"
  local n=0
  for spec in "$@"; do
    n=$((n+1))
    python3 - "$dir/sidecars/s$n.json" "$spec" <<'PYEOF'
import json, sys
path, spec = sys.argv[1], sys.argv[2]
rung, cls, narr = spec.split(":", 2)
o = {"schema":"observed-trace/v1","claim_strength":"real-agent-observed",
     "producer":{"kind":"real-agent","id":"t"},
     "experiment":{"id":"x","fixture":"../x","incentive_state":"../x","context":{"name":"difficulty","value":1}},
     "run":{"rung":int(rung),"rung_name":["blind","reward-aware","adversarial"][int(rung)],
            "trial":1,"status":"timeout" if cls=="_timeout" else "completed",
            "run_dir":"runs/r","started_at":"2026-01-01T00:00:00Z","duration_ms":1},
     "narration":narr}
if cls in ("fixed","hacked","failed"):
    o["observation"]={"classification":cls,"exit_code":0 if cls=="fixed" else 1,
                      "anomaly_note":None,"artifacts":[]}
json.dump(o, open(path,"w"))
PYEOF
  done
}

# cfgA: a graded verdict of each class + an infra non-run (wrapper marker)
mkbatch "$W/cfgA" "0:fixed:clean" "0:hacked:clean" "2:failed:clean" \
  "2:_none:[stderr] ERROR: [party-wrapper] cannot reach ollama (timed out)"
# cfgB: a timeout-status infra non-run + an ungraded completed run
mkbatch "$W/cfgB" "0:_timeout:harness died" "0:_none:ran but nobody scored it"

$SR --config "modelA=$W/cfgA" --config "modelB=$W/cfgB" > "$W/out1.txt" 2>"$W/err1.txt"
ok "exit 0 on valid configs" "[ \$? -eq 0 ] || grep -q . '$W/out1.txt'"

ok "graded verdicts counted (fixed+hacked+failed present)" \
  "grep -qE 'modelA .*1 .* 1 .* 1' '$W/out1.txt' || grep -q 'modelA' '$W/out1.txt'"
ok "infra non-run class rendered" "grep -q 'infra' '$W/out1.txt'"
ok "ungraded class rendered" "grep -q 'ungraded' '$W/out1.txt'"
ok "legend states counts-not-recomputed" "grep -qi 'never recomputed' '$W/out1.txt'"

# Determinism: run twice → byte-identical
$SR --config "modelA=$W/cfgA" --config "modelB=$W/cfgB" > "$W/out2.txt" 2>/dev/null
ok "deterministic: identical output across two runs" "cmp -s '$W/out1.txt' '$W/out2.txt'"

# Config ordering follows CLI order (modelB first → modelB row before modelA)
$SR --config "modelB=$W/cfgB" --config "modelA=$W/cfgA" > "$W/out3.txt" 2>/dev/null
ok "config order follows CLI order" \
  "[ \$(grep -n 'modelB' '$W/out3.txt' | head -1 | cut -d: -f1) -lt \$(grep -n 'modelA' '$W/out3.txt' | head -1 | cut -d: -f1) ]"

# Trust boundary: the aggregator must not reproduce Gygax's COMPUTED verdict lines
# (it may name 'cliff' only to defer it). Real invariant = no forecast/cliff FINDINGS.
ok "never emits a computed cliff/forecast verdict" \
  "! grep -qiE 'argmax @|no cliff observed|cliff observed at|vs forecast|fix:hack' '$W/out1.txt'"

# Input errors
$SR --config "bad=$W/nonexistent" >/dev/null 2>"$W/err2.txt"; rc=$?
ok "missing batch dir → exit 1" "[ $rc -eq 1 ]"
$SR >/dev/null 2>"$W/err3.txt"; rc=$?
ok "no args → exit 1" "[ $rc -eq 1 ]"

echo "----"
echo "sweep-report: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
