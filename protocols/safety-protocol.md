# Safety Protocol

> Non-negotiable safety contract for all domains, all sessions, all modes. No opt-out.

**Version:** 1.0
**SDD Reference:** sdd.md Section 3.1.4
**PRD Reference:** FR-C4, NFR-5, NFR-6

---

## Principle

Safety is core infrastructure, not a domain concern. Every domain inherits this protocol. No domain may weaken it. A domain MAY add domain-specific boundaries on top.

## Pre-Session Agreement

**Mandatory. Cannot be skipped.**

Before any creative generation begins, the session skill MUST:

1. Present the safety agreement to the practitioner:
   - **Lines**: Content that will not appear at all.
   - **Veils**: Content that may be implied but not depicted.
   - **X-card**: Confirmation that X-card is active (retract last content on trigger).
   - **Domain boundaries**: Any additional boundaries declared by the domain vertical.
2. Wait for explicit confirmation.
3. Record the agreement in the sidecar preamble (`safety_agreement` field).

If the practitioner declines the safety agreement, the session does not start.

## In-Session Commands

These commands are available at ALL times during an active session:

| Command | Effect |
|---------|--------|
| `/pause` | Halt session immediately. Log `pause` event. No final sentence. |
| `/x-card` | Retract last generated content. Log `safety_trigger` event. Resume from safe point. |
| `/resume` | Resume session from last safe point after pause or X-card. |

## Safety-as-Data

Safety events are **findings**, not just interruptions:

- Every safety trigger is captured in the sidecar as a `safety_trigger` event (from session-events-base).
- Safety triggers surface in digests as design data.
- In TTRPG, safety triggers surface as `dead_design_space` findings — regions of the game-state that this practitioner/table cannot safely render.
- The `dead_design_space_flag` field (default: true) marks triggers that represent design constraints.

## Content Rules

- Arneson does not generate content outside the safety agreement, regardless of what the structured state permits.
- Arneson does not voice children in harm.
- Arneson does not narrate sexual violence on-stage.
- These rules are absolute and not configurable.

## Domain Extensions

A domain vertical MAY:
- Add domain-specific boundaries (via `schemas/core/safety.schema.yaml` `domain_boundaries` field).
- Add domain-specific safety trigger types (via the domain's session-events extension).

A domain vertical MUST NOT:
- Remove or weaken any base safety requirement.
- Make the pre-session agreement optional.
- Disable X-card or pause functionality.
