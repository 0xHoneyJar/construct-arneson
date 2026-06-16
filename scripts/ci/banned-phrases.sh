# banned-phrases.sh — the single ban-list source of truth (cycle-004).
# Sourced by both scripts/ci/banned-copy-check.sh (the CI gate over docs + report
# wording) and domains/agent-systems/scripts/test-gap-report.sh (the gate over
# generated gap-report output). One list so the two can never drift.
# These overclaiming phrases (sandbox-limits §A/B) may appear ONLY inside the
# quoted ban-list table in domain.conventions.md. The "say instead" guidance lives
# there too. No side effects: this file only assigns BANNED.
BANNED='hard metrics|zero hallucination|high-fidelity|proves it'"'"'?s compelling|validates your incentives|effectively real|as good as observed'
