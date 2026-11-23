#!/usr/bin/env bash
# One-time GitHub setup: labels and the project board.
# Run from the repo root AFTER the GitHub repo exists and is set as `origin`.
# Needs: gh auth login (with the "project" scope for the board:
#        gh auth refresh -s project)
set -euo pipefail

label() { gh label create "$1" --color "$2" --description "$3" --force; }

label "team:rep"  "1f77b4" "Team 1 - Representation"
label "team:ret"  "2ca02c" "Team 2 - Retrieval"
label "team:gen"  "9467bd" "Team 3 - Generation"
label "team:eval" "ff7f0e" "Team 4 - Eval and integration"
label "team:lead" "7f7f7f" "Foundation work by the leads"
label "size:S"    "c5def5" "Up to 1 day"
label "size:M"    "0e8a16" "2-3 days"
label "should"    "fbca04" "Drop before any must slips"
label "blocked"   "d73a4a" "Waiting on another issue"
label "good first issue" "7057ff" "Good for a fresher"

# Project board (owner = the org or user that owns the repo).
OWNER="${1:-}"
if [[ -n "$OWNER" ]]; then
  gh project create --owner "$OWNER" --title "Vanilla RAG - 18 days"
  echo "Board created. Add Status columns: To do, In progress, Review, Done."
else
  echo "Labels done. To also create the board: $0 <org-or-user>"
fi
