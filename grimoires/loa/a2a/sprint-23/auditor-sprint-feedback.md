# Security & Quality Audit — cycle-007 Sprint 1 (global 23): FR-1 decision-trace emitter

**Verdict: APPROVED - LETS FUCKING GO**

Paranoid review of the actual code (not the report). No CRITICAL / HIGH / MEDIUM findings. One LOW
(robustness, already logged by the reviewer). This sprint *strengthens* the construct's integrity posture.

## Attack-surface review

| Surface | Finding |
|---------|---------|
| **Input parsing** | Sidecar parsed via `restricted_yaml` (the repo's safe stdlib parser — not `yaml.load`; no arbitrary object construction). ✓ |
| **Path traversal (output)** | Filenames are built from `_sanitize(corpus_id)` (`emit_decision_trace.py:340`), which strips every non-`[A-Za-z0-9._-]` char (incl. `/`), and the `-{t}.json` suffix guarantees the name is never `.`/`..`. Verified: a hostile `scenario_id` like `../../etc/passwd` yields the literal in-dir filename `..-..-etc-passwd-run-0.json` — no separator survives, so `out / fname` cannot escape. ✓ |
| **Path traversal (input)** | Unlike its sibling `project_trace.py`, the emitter does **not** resolve `preamble.state_path` to a filesystem path — it reads only the operator-supplied `--in` file. Strictly fewer traversal surfaces than the sibling. ✓ |
| **Code execution** | No `eval`/`exec`/`subprocess`/`os.system`/`popen`/`socket`/`urllib` — only `Path.read/write_text` + `json`/`hashlib`/`re` (paranoid grep clean). ✓ |
| **Secrets** | None. No credentials/keys/tokens in script or fixtures; fixtures are synthetic (`construct_git_sha` is all-zeros). ✓ |
| **Info disclosure** | Errors go to stderr with an `ERROR: [emit_decision_trace]` prefix; the drift message prints only 12-char sha prefixes; no stack traces or secrets leaked. ✓ |
| **Determinism** | No `datetime.now()`/`random`; sorted-key output — audit-friendly and replayable. ✓ |

## Integrity controls this sprint ADDS (credit)

1. **Supply-chain integrity**: the vendored Gygax contract is a sha-pinned, read-only byte-copy; the
   emitter's `vendor_selfcheck` (`emit_decision_trace.py:85-115`) refuses to run (exit 2) on pin drift,
   and `vendor-drift-guard.sh` byte-diffs all four files against upstream. A tampered vendored contract
   is caught loudly.
2. **Claim integrity (NFR-5)**: the producer-bound claim rule (`validate_record` `:241-249`) makes it
   *structurally impossible* for a simulation to launder its output as `real-agent-observed`.
   `claim_strength`/`producer.kind` are hardcoded literals, never input-derived. This is the construct's
   core trust contract (the judge must never be able to mistake forecast for observed evidence) — and
   it's enforced, not just documented.

## Findings

- **LOW (robustness, non-blocking):** `build_records` does not type-guard `events`
  (`emit_decision_trace.py:301`) — a malformed sidecar with `events:` as a mapping would raise
  `AttributeError` rather than a clean `exit 1`. Not a security vuln (input is operator-supplied; worst
  case is a self-crash, no injection path). Matches the sibling `project_trace.py`. Already logged as
  reviewer Concern 2; carry to the hardening cycle.

## Decision

All acceptance criteria met, senior review approved, no security blockers, integrity posture improved.
**APPROVED.** COMPLETED marker created; ledger sprint-23 → completed.
