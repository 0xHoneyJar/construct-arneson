# Sprint 1 Security Audit — Auditor Feedback

**Sprint**: sprint-1 (Foundation / M0)
**Auditor**: /audit-sprint skill (Paranoid Cypherpunk Auditor)
**Date**: 2026-04-13
**Verdict**: **APPROVED - LETS FUCKING GO**

---

## Threat Model Context

Sprint 1 is **scaffolding** — YAML schemas, identity files, CI scripts, directory structure.
No application code. No network services. No user-facing execution. No auth surfaces. No
PII handling. The CI has never been pushed to GitHub Actions; all validation was local.

Threat model for Sprint 1: supply-chain risk from CI dependencies, and process hygiene
(HEKATE isolation, secrets discipline). That's the meaningful attack surface.

---

## Findings

### CLEAN: Secrets Scan

Comprehensive scan of all non-.git, non-.loa, non-.beads files for API keys, passwords,
tokens, private keys, embedded credentials, webhook URLs, .env files, JWT patterns,
and hardcoded user paths.

**Result: CLEAN.** Zero credentials, secrets, or sensitive data found in any tracked file.
The `.gitignore` properly excludes framework state directories. No `.env` files exist.

---

### HIGH: yq Binary Download Without Integrity Verification

**File**: `.github/workflows/ci.yaml:28,80`
**Severity**: HIGH (downgraded from CRITICAL — no production deployment, ephemeral runners)

```yaml
sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
```

**Issues**:
- No version pin (`/latest/download/` resolves to whatever's current)
- No SHA256 checksum verification
- No GPG signature check
- `sudo` writes to system binary path

**Risk**: Attacker with GitHub Releases write access (or MITM on CDN) serves malicious
binary that runs with runner permissions on every CI invocation.

**Actual blast radius (Sprint 1)**: Low. CI has never run. No secrets in repo for a
compromised binary to exfiltrate. But this pattern would become CRITICAL if carried
into Sprint 2+ where CI runs regularly.

**Required fix for Sprint 2 start**:
```yaml
- name: Install yq (v4.50.1 pinned)
  run: |
    YQ_VERSION="v4.50.1"
    YQ_SHA256="<known hash>"
    wget -qO /tmp/yq "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64"
    echo "${YQ_SHA256}  /tmp/yq" | sha256sum -c -
    chmod +x /tmp/yq
    sudo mv /tmp/yq /usr/local/bin/yq
    yq --version
```

**Status**: Non-blocking for Sprint 1 approval (CI has not been pushed). **Mandatory
fix before first CI push in Sprint 2.**

---

### MEDIUM: GitHub Actions Security Hardening

**File**: `.github/workflows/ci.yaml`
**Severity**: MEDIUM

**Issues**:
- `runs-on: ubuntu-latest` — unpinned runner; could drift
- `actions/checkout@v4` — not pinned to exact commit SHA
- No explicit `permissions:` block limiting job scope

**Recommended fix** (Sprint 2):
```yaml
permissions:
  contents: read

jobs:
  arneson-alone:
    runs-on: ubuntu-24.04   # pinned
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

**Status**: Non-blocking. Standard hardening practice. Carry into Sprint 2.

---

### MEDIUM: Error Suppression in Validation Scripts

**Files**: `scripts/ci/validate-construct.sh:38`, `validate-schemas.sh:32`, `validate-fallbacks.sh:37`
**Severity**: MEDIUM

```bash
value=$(yq eval "$field" "$MANIFEST" 2>/dev/null)
```

Suppressing stderr means a corrupt YAML file produces the same signal as a missing field.
Both yield `FAIL: missing required field` but the root cause differs and the fix differs.

**Recommended fix**: Separate the cases:
```bash
value=$(yq eval "$field" "$MANIFEST" 2>&1) || { echo "WARN: yq error on $field: $value"; FAIL=1; continue; }
```

**Status**: Non-blocking. Improve in Sprint 2.

---

### LOW: HEKATE Audit Filter Fragility

**File**: `scripts/ci/hekate-audit.sh:41-52`
**Severity**: LOW

Multi-pipe grep chain is hard to reason about. A dedicated allow-list file would be
cleaner and more auditable than inline regex exclusions.

**Status**: Non-blocking. Track for future refactor.

---

### LOW: No Cryptographic Audit Trail

**Files**: All `scripts/ci/validate-*.sh`
**Severity**: LOW

Validation scripts produce human-readable `OK:` output but no machine-verifiable trail
(e.g., checksums of validated files). Cannot later prove "this exact construct.yaml passed
validation at this time."

**Status**: Non-blocking. Nice-to-have for v2.

---

### INFORMATIONAL: `sudo` Usage in CI

The `sudo` in `sudo wget -qO /usr/local/bin/yq` and `sudo chmod +x` is standard for
GitHub Actions runners (writing to system paths requires elevation on ubuntu runners).
While installing to a user-owned path (`$HOME/.local/bin`) would be cleaner, this is
not a vulnerability — it's a style preference. Downgraded to informational.

---

## Security Posture Summary

| Area | Status | Notes |
|------|--------|-------|
| Secrets / credentials | CLEAN | Zero findings |
| PII / sensitive data | CLEAN | No user data anywhere |
| Supply chain (CI) | HIGH (1 finding) | yq download needs pin + checksum |
| Input validation | MEDIUM | Error suppression in validators; safe for hardcoded inputs |
| HEKATE isolation | PASS | Audit script works; filter is fragile but functional |
| Network exposure | N/A | No network services in Sprint 1 |
| Auth/Authz | N/A | No auth surfaces in Sprint 1 |
| File permissions | CLEAN | Scripts are +x; no setuid/setgid |
| OWASP Top 10 | N/A | No web application; not applicable to skill-pack |

---

## HEKATE Isolation Audit

Special-focus audit per NOTES.md directive (2026-04-13):

- [x] `scripts/ci/hekate-audit.sh` runs and returns clean
- [x] No MIBERA/HEKATE content references in: construct.yaml, identity/, schemas/, resources/archetypes-fallback/, examples/synthetic-fixture/game-state.yaml
- [x] Meta-references (the phrase "HEKATE-free", the CI job name "HEKATE audit") are filtered correctly
- [x] `examples/synthetic-fixture/` is verifiably HEKATE-free per `validate-fixture.sh` secondary check
- [x] `grimoires/loa/context/` files DO reference HEKATE (original proposal) — these are correctly excluded from the audit scope

**HEKATE isolation: PASS.**

---

## Sprint 1 Mandatory Fixes Before Sprint 2

| Fix | Severity | Blocking? |
|-----|----------|-----------|
| Pin yq version + verify SHA256 in CI workflow | HIGH | **Yes — before first CI push** |
| Pin actions/checkout to commit SHA | MEDIUM | No — but should accompany yq fix |
| Add `permissions: contents: read` to workflow | MEDIUM | No — but should accompany yq fix |

These are Sprint 2 intake tasks, not Sprint 1 re-work. Sprint 1 Foundation is approved
as-is because CI has not been pushed yet.

---

## Verdict

**APPROVED - LETS FUCKING GO**

Sprint 1's security posture is clean for scaffolding. Zero secrets, zero PII, HEKATE
isolation verified. The supply-chain risk (yq download) is real but contained: CI hasn't
been pushed, and the fix is straightforward. Mandatory yq pin lands in Sprint 2 start
before the first CI invocation on GitHub.

The construct is ready for Sprint 2 (Vertical Slice `/braunstein`).

---

*Audited by /audit-sprint, 2026-04-13*
