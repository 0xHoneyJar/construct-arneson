#!/usr/bin/env bash
# HEKATE audit: zero-tolerance grep for MIBERA/HEKATE references.
# Per NOTES.md user directive (2026-04-13): MIBERA: HEKATE is private/upstream and
# must not appear in construct-arneson code, examples, tests, or docs.
#
# The audit looks for REAL references to HEKATE as a game. Meta-references that
# document the exclusion (the phrase "HEKATE-free", the job name "HEKATE audit",
# sentences explaining why we don't use it) are permitted and filtered out.
#
# Exit 1 if ANY real match found.

set -euo pipefail

# Directory-level excludes: areas where HEKATE may appear as historical/meta context.
EXCLUDE_DIRS=(
  --exclude-dir=.git
  --exclude-dir=.loa              # upstream Loa framework; not our code
  --exclude-dir=node_modules
  --exclude-dir=.beads
  --exclude-dir=context           # grimoires/loa/context/ — original proposal may reference HEKATE
  --exclude-dir=analytics         # grimoires/loa/analytics/ — runtime log of past prompts
  --exclude-dir=prototypes        # grimoires/loa/prototypes/ — sprint prototypes that explain exclusion
  --exclude-dir=ci                # scripts/ci/ — audit scripts that contain the search patterns themselves
)

# File-level excludes: specific files where meta-references are expected.
EXCLUDE_FILES=(
  --exclude=hekate-audit.sh       # this script
  --exclude=NOTES.md              # decision log references the exclusion directive
  --exclude=prd.md                # planning doc references exclusion
  --exclude=sdd.md                # planning doc references exclusion
  --exclude=sprint.md             # planning doc references exclusion
)

# Find raw matches.
RAW_MATCHES=$(grep -rInI "${EXCLUDE_DIRS[@]}" "${EXCLUDE_FILES[@]}" -E 'mibera|hekate' . 2>/dev/null || true)

# Filter out legitimate meta-references:
#   "HEKATE-free"          — documents that we don't use it
#   "HEKATE audit"         — the name of this check / the CI job name
#   "like MIBERA: HEKATE"  — explaining why it's excluded
#   "MIBERA HEKATE is"     — explanatory context (e.g., in permission allowlists)
FILTERED_MATCHES=$(echo "$RAW_MATCHES" | grep -viE 'hekate[- ](free|audit)' \
                                        | grep -viE 'like (mibera|hekate)' \
                                        | grep -viE '(mibera|hekate)[- ]is' \
                                        | grep -viE 'exclude.*(mibera|hekate)' \
                                        | grep -viE 'no.*(mibera|hekate)' \
                                        | grep -viE '(mibera|hekate)-(less|exclusion)' \
                                        | grep -viE 'without.*(mibera|hekate)' \
                                        | grep -viE 'hekate-audit\.sh' \
                                        | grep -viE 'permission_audit' \
                                        || true)

if [ -n "$FILTERED_MATCHES" ]; then
  echo "FAIL: HEKATE audit found non-meta references to MIBERA/HEKATE:"
  echo ""
  echo "$FILTERED_MATCHES"
  echo ""
  echo "construct-arneson must be HEKATE-free per NOTES.md directive 2026-04-13."
  echo "If a real reference is needed, it is probably a bug. If a meta-reference is misfiring"
  echo "the filter, extend scripts/ci/hekate-audit.sh with additional meta-exclusion patterns."
  exit 1
fi

echo "OK: HEKATE audit clean — no real MIBERA/HEKATE references found."
