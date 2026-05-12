# Security Audit -- construct-arneson v2 (Full Cycle)

**Auditor:** Security (paranoid cypherpunk review)
**Date:** 2026-05-12
**Scope:** All shippable files -- schemas, skills, protocols, identity, CI, extension story, examples, scripts
**Prior gate:** Engineer review approved with 5 noted concerns (C-1 through C-5)
**Verdict:** **APPROVED - LETS FUCKING GO**

---

## Threat Model

This is a Loa framework skill-pack construct. There is no backend, no API, no database, no user auth, no network calls. The runtime is Claude Code + Loa. The "database" is the filesystem. The attack surface is:

1. Secrets/credentials leaking into the repo
2. Path traversal via YAML fields referencing `../` or absolute paths
3. Safety bypass via domain extension overriding core safety infrastructure
4. Content injection via malicious YAML in domain verticals
5. CI supply chain (GitHub Actions pinning, yq binary integrity)
6. HEKATE/PII leakage into shippable files
7. Identity refusal bypass via domain vertical
8. Extension story attack surface (malicious domain overriding core)

---

## Findings

### MEDIUM: CI yq Download Lacks SHA256 Verification

**File:** `.github/workflows/ci.yaml:26-33, 88-95, 141-148`

The step name says "v4.50.1 pinned with integrity check" but the step does NOT perform an integrity check. The binary is downloaded via `wget` from GitHub Releases and executed without SHA256 verification. The version is pinned (good), but a compromised GitHub Release or MITM on the download could substitute a malicious binary.

```yaml
YQ_URL="https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64"
wget -qO /tmp/yq "$YQ_URL"
chmod +x /tmp/yq
sudo mv /tmp/yq /usr/local/bin/yq
```

**Risk:** An attacker who compromises the yq GitHub release page, or who MITMs the download (HTTPS makes this unlikely but not impossible in CI environments with proxy configurations), could execute arbitrary code in the CI runner. The CI runner has read access to the repository and could exfiltrate contents.

**Mitigation:** Add SHA256 verification after download:
```yaml
YQ_SHA256="expected_hash_here"
echo "$YQ_SHA256  /tmp/yq" | sha256sum -c -
```

The step name claiming "integrity check" when none exists is itself a concern -- it creates false confidence.

**Severity:** MEDIUM. The version pin prevents drift. HTTPS prevents casual MITM. But the claim of integrity checking is misleading, and supply-chain attacks on CI binaries are a real vector.

### MEDIUM: GitHub Actions Not Pinned to SHA

**File:** `.github/workflows/ci.yaml:22, 84, 137`

`actions/checkout@v4` is pinned to a mutable tag, not a commit SHA. Tag-based pinning means the action code can change without your CI config changing. The `actions/checkout` action is controlled by GitHub and is high-trust, but the security-paranoid posture is to pin to SHA:

```yaml
# Current (tag-pinned, mutable):
- uses: actions/checkout@v4

# Recommended (SHA-pinned, immutable):
- uses: actions/checkout@<sha256>  # v4.x.x
```

**Severity:** MEDIUM. This is `actions/checkout` specifically (GitHub-owned, high trust), not a third-party action. The practical risk is low. But the principle matters: if this construct later adds third-party actions, the precedent is tag-pinning, which is insufficient for untrusted publishers.

### LOW: `grounding_state_path` and `state_path` Accept Arbitrary Relative Paths

**Files:** `schemas/core/voice-base.schema.yaml:115-118`, `schemas/core/session-events-base.schema.yaml:34-37`

Both `grounding_state_path` (in voice files) and `state_path` (in session preambles) are free-form string fields with no path validation constraints. A malicious or misconfigured voice file could declare `grounding_state_path: ../../../etc/passwd` and the persona-hosting protocol instructs Arneson to "load the structured state the persona grounds against."

**Mitigation factors:**
- The runtime is Claude Code, which reads files via tool calls that are subject to user HITL approval and sandbox constraints.
- Claude Code will not silently read `/etc/passwd` and inject it into fiction.
- The protocol says "If the path doesn't exist, warn the practitioner."
- There is no code that programmatically opens these paths -- they are consumed by the LLM agent, which has its own safety layer.

**Recommendation:** Add a validation rule to voice-base: "grounding_state_path MUST be a relative path within the project root. Paths containing `..` are invalid." This is defense-in-depth even though the runtime prevents exploitation.

**Severity:** LOW. The LLM-as-runtime architecture means path traversal is not exploitable in the traditional sense. But the schema should declare the constraint anyway.

### LOW: `player_name` Referenced in domain.conventions.md but Not in Schema

**File:** `domains/ttrpg/domain.conventions.md:40`

The domain conventions document mentions `player_name` as a field on PC voice files ("PCs: `pc_ref`, `player_name`, `player_consent`"), but `voice-pc.schema.yaml` does NOT define a `player_name` field. The field was apparently removed or renamed to `pc_ref` during the v2 refactor.

**PII concern:** If the field existed as documented, it would store a real person's name in a YAML file that could be committed to git. The schema's actual implementation is correct -- it has `pc_ref` (a stable identifier) and `player_consent_metadata` (consent boundaries), with no field for the player's real name.

**Recommendation:** Fix `domain.conventions.md:40` to match the actual schema: replace `player_name` with the actual field names.

**Severity:** LOW. The schema is correct. The documentation is wrong in a direction that could mislead a domain author into adding a PII field.

### LOW: `voice-pc.schema.yaml` Allows `x_card_active: false`

**File:** `domains/ttrpg/schemas/voice-pc.schema.yaml:44-45`

The schema allows `x_card_active: false` on a PC voice file. The safety-protocol.md says safety is "non-negotiable" and x-card commands "MUST be available in every session." There is a mitigation: the validation rule at line 67 says "When x_card_active is false, arneson logs a warning at session open." But this is a LOG, not a BLOCK.

**Risk:** A designer could create a PC voice file with `x_card_active: false`, and Arneson would proceed with a warning rather than refusing. This creates a path where a session runs without the x-card safety mechanism. The safety schema says the x-card must always be available, but the PC schema allows it to be disabled.

**Mitigation:** The `safety.schema.yaml` validation rule says "Safety commands (/pause, /x-card, /resume) MUST be available in every session regardless of domain." This overrides the PC-level field. The field on the PC is about whether the PC's AUTHOR has opted in, not whether the SESSION has x-card available. The session-level safety agreement (from session-events-base) has `x_card_active: true` as default. These are two different layers.

**Recommendation:** Add a comment to voice-pc.schema.yaml clarifying that `x_card_active: false` disables automatic loading of THIS PC's consent lines into the session agreement, but does NOT disable the session-level x-card. If the intent is that x_card_active on a PC can actually disable the session x-card, this is a safety protocol violation and should be changed to always-true.

**Severity:** LOW. The schema layering means this is unlikely to actually disable x-card at the session level. But the ambiguity should be resolved.

---

## Clean Passes

### Secrets/Credentials: PASS

Comprehensive grep for `sk-`, `ghp_`, `AKIA`, `password=`, `secret=`, `token=`, `api_key`, `Bearer`, `Authorization` across all construct files (excluding `.loa/` submodule):

- **Zero hits in shippable files** (schemas, domains, skills, protocols, identity, scripts, examples, construct.yaml).
- One hit in `grimoires/loa/a2a/sprint-1/engineer-feedback.md` -- the word "fragment" contains the substring, not a secret. Verified: false positive from grep matching "to fragment against".
- No `.env` files, no credentials files, no API key patterns anywhere in the construct.

### Path Traversal in YAML: PASS

Grep for `../` across all YAML files in the construct: **zero hits**. No YAML file references a parent directory. All paths in construct.yaml, schemas, and skill index files are relative-within-project paths (e.g., `schemas/core/safety.schema.yaml`, `domains/ttrpg/schemas/...`). No absolute paths found in any YAML file.

### HEKATE/PII Isolation: PASS

```bash
grep -ri "hekate" schemas/ domains/ skills/ protocols/ identity/ construct.yaml examples/ scripts/
# Zero hits

grep -ri "MIBERA\|mibera" schemas/ domains/ skills/ protocols/ identity/ construct.yaml examples/ scripts/
# Zero hits
```

HEKATE and MIBERA references exist only in `grimoires/loa/` (development notes, PRD, SDD, prior audit reports, context documents) -- these are non-shippable planning artifacts. Zero contamination in any file that ships as part of the construct.

No personal email addresses, real names, or identifying information found in shippable files. The `player_name` field does not exist in the actual schema (see LOW finding above).

### Safety Protocol Enforcement: PASS

The safety architecture is layered and consistent:

1. **Schema level** (`safety.schema.yaml`): `agreement_required: true` with explicit "Cannot be set to false." Validation rule: "pre_session.agreement_required MUST be true -- no override permitted."
2. **Protocol level** (`safety-protocol.md`): "Mandatory. Cannot be skipped." Absolute content rules (no children in harm, no sexual violence on-stage) declared as "not configurable."
3. **Session lifecycle** (`session-lifecycle.md`): SafetyPrompt is the SECOND state -- no path from Invoked to Active that bypasses it.
4. **Identity level** (`ARNESON.md`): Safety declared as "non-negotiable. Every domain, every session, every mode. No opt-out."
5. **Extension interface** (`safety-protocol.md`): "A domain vertical MUST NOT: Remove or weaken any base safety requirement. Make the pre-session agreement optional. Disable X-card or pause functionality."

A domain vertical can ADD boundaries but cannot REMOVE base boundaries. The `domain_boundaries` field in safety.schema.yaml is additive-only by declaration.

### Identity Refusal Enforcement: PASS

Refusals are structurally enforced at multiple layers:

1. **Identity file** (`refusals.yaml`): 7 refusal categories with `vocabulary_to_avoid` lists.
2. **Audit configuration** (`refusals.yaml:92-101`): Automated scan targets, scan mode (in-archetype-voice only), violation severity HIGH, violation action flag_for_review.
3. **Skill-level reinforcement** (`braunstein/SKILL.md:193-205`): "What You Must Not Do" section references refusals.yaml explicitly.
4. **Identity prose** (`ARNESON.md`): Refusals described as "load-bearing commitments."

A domain vertical cannot override refusals because refusals live in `identity/refusals.yaml` (construct-level, not domain-level) and are loaded at construct initialization, not at domain initialization. There is no mechanism in the extension interface to modify or suppress refusals.

### Extension Story Attack Surface: PASS

The domain extension contract is additive-only by design:

- **Schema extension**: Domain schemas declare `extends: voice-base` (or `session-events-base`, `digest-base`). The base schema fields are inherited, not overridable. The `additional_fields` and `additional_event_types` naming convention makes clear that domains ADD, they do not REPLACE.
- **Safety protocol**: Domain skills MUST declare `safety-protocol` in their `index.yaml` `protocols` list. The CI extension-story job validates this (`ci.yaml:188-196`).
- **Core isolation**: The extension-story CI job verifies core directories exist unchanged. (The engineer review noted this check is structural, not mutation-based -- see C-3 -- but the architectural constraint is sound.)
- **No code execution**: Domain schemas are declarative YAML consumed by an LLM. There is no `eval()`, no template expansion, no code generation from YAML values. A malicious YAML value becomes a string the LLM reads, not code the LLM executes.

A malicious domain vertical could:
- Declare nonsense schema fields (benign -- ignored by core)
- Omit safety-protocol from its index.yaml protocols (caught by CI)
- Include `../` in a path field (mitigated by LLM runtime; see LOW finding above)
- Include injection text in YAML string values (mitigated by LLM's own safety layer; the YAML is context for the LLM, not executable input)

The meaningful attack surface is social engineering the LLM via crafted YAML values, which is an LLM-layer concern (Claude's own safety training), not a construct-layer concern.

### Content Injection via YAML: PASS

The construct's YAML files are consumed by Claude Code as context, not parsed by a YAML-to-code pipeline. There is no:
- YAML alias/anchor abuse vector (no `*merge` keys, no `<<:` patterns in schemas)
- Template injection vector (no `${variable}` expansion in any YAML)
- Code execution vector (no `!!python/object` or similar type tags)

YAML values are read as strings by the LLM agent. The worst a malicious YAML value can do is mislead the LLM -- which is bounded by Claude's own safety training and the construct's safety protocol.

---

## CI Security Summary

| Check | Status | Notes |
|-------|--------|-------|
| Actions pinned | MEDIUM | Tag-pinned (@v4), not SHA-pinned |
| yq integrity | MEDIUM | Version pinned, no SHA256 verification despite step name claiming "integrity check" |
| Secrets in CI | PASS | No secrets in workflow files |
| Permissions | PASS | No elevated permissions requested |
| Third-party actions | PASS | Only `actions/checkout` (GitHub-owned) |

---

## Verdict Matrix

| Category | Verdict | Findings |
|----------|---------|----------|
| Secrets/credentials | PASS | Zero secrets in shippable files |
| Path traversal | PASS (with LOW) | Zero `../` in YAML; schema lacks path constraint |
| Safety protocol bypass | PASS | Multi-layer enforcement; additive-only extension |
| Content injection | PASS | No code-execution vector; LLM-as-runtime bounds risk |
| CI security | MEDIUM x2 | yq SHA missing; actions not SHA-pinned |
| HEKATE/PII | PASS | Zero contamination in shippable files |
| Identity refusal bypass | PASS | Construct-level, not overridable by domain |
| Extension attack surface | PASS | Additive-only by design; CI validates protocol compliance |

---

## Final Verdict

**APPROVED - LETS FUCKING GO**

All findings are MEDIUM or LOW. The two MEDIUM findings (yq integrity and actions pinning) are CI supply-chain hardening items that do not affect the construct's runtime security posture. They should be addressed in v2.1 or a quick follow-up PR. The LOW findings are defense-in-depth improvements.

The construct's security architecture is sound. Safety is structurally non-bypassable. The extension story is additive-only. No secrets, no PII, no HEKATE leakage. The LLM-as-runtime architecture eliminates entire classes of traditional vulnerabilities (SQL injection, XSS, SSRF, etc.) while introducing a different class (prompt injection via YAML context) that is bounded by Claude's own safety layer.

Ship it.

---

*Security audit by paranoid cypherpunk reviewer, 2026-05-12*
