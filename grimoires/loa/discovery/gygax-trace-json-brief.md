# Brief for construct-gygax: a `--json` reporting flag on the trace CLI

**Date:** 2026-06-10 · **From:** construct-arneson v4.1 Sprint 2 (OQ-1 resolution)
**Class:** reporting nit, NOT a contract change. Low priority — Arneson has a clean path without it.

## Context
Arneson's `/playout --sweep` aggregates results across N configs into a cross-config triaged
table. The per-config grades it needs are already in the graded sidecars (JSON the scorer
writes on `--regrade`), so the sweep reads those directly — no blocker.

What's MD-only today is the *interpretation* layer: `trace/index.ts` renders the per-rung
table, `withinNoise` wording, cliff detection, and severity as Markdown to stdout
(index.ts:77-92 — flags are --incentive-state/--context/--fixture/--regrade only). To carry
Gygax's cliff/within-noise wording verbatim into a cross-config view, Arneson would have to
brittle-parse that Markdown — which it deliberately won't.

## The ask (optional)
Add a `--json` flag to `trace/index.ts` that emits the same report as a structured object:
per-rung `{rung, rung_name, counts:{fixed,hacked,failed}, ratio, within_noise}`, plus
`cliff` and `severity`. Same data the Markdown already computes — just machine-readable.

## Why it's worth it (eventually)
It lets the analyst's *interpretation* (not just raw counts) compose across configs without
anyone re-implementing cliff/within-noise logic — preserving the single-source-of-truth
boundary (Arneson counts, Gygax judges). Until then, Arneson carries counts only and links to
Gygax's per-config report for the interpretation.

## Not urgent
No Arneson work is blocked. File when convenient.
