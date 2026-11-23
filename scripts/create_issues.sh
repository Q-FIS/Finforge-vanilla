#!/usr/bin/env bash
# Create one GitHub issue per file in issues/ (except README.md).
# Run from the repo root, after scripts/setup_github.sh (the labels must exist).
#
# Each issue file looks like:
#   line 1:  # [REP-01] Title
#   line 2:  labels: team:rep, size:M
#   line 3+: the body
#
# Usage:  scripts/create_issues.sh            (creates all)
#         scripts/create_issues.sh --dry-run  (only prints what it would do)
set -euo pipefail

DRY_RUN="${1:-}"
for file in issues/*.md; do
  [[ "$(basename "$file")" == "README.md" ]] && continue
  title="$(head -n 1 "$file" | sed 's/^# //')"
  labels="$(sed -n '2p' "$file" | sed 's/^labels: //; s/, /,/g')"
  body="$(tail -n +3 "$file")"
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "would create: $title   [labels: $labels]"
  else
    gh issue create --title "$title" --label "$labels" --body "$body"
  fi
done
