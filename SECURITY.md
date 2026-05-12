# Security Policy

## Safety-First Design

construct-arneson generates creative fiction. Safety is a core architectural concern, not an afterthought:

- **Pre-session safety agreement** is mandatory and cannot be skipped (see `protocols/safety-protocol.md`).
- **In-session safety commands** (/pause, /x-card, /resume) are always available.
- **Safety events are data** — logged as structured findings, not just social interruptions.
- **Content boundaries** are configurable per session and per domain.
- **No domain may weaken** core safety requirements.

## Reporting a Vulnerability

If you discover a security vulnerability in construct-arneson, please report it responsibly:

1. **Do not** open a public issue.
2. Email the maintainers directly or use GitHub's private vulnerability reporting.
3. Include a clear description of the vulnerability and steps to reproduce.

## Scope

This security policy covers:
- The construct's schema validation and enforcement
- Safety protocol implementation
- Identity refusal enforcement
- Content generation boundaries

This policy does not cover:
- The Loa framework itself (report to the Loa project)
- Claude Code or the Claude API (report to Anthropic)
