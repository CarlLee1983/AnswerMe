#!/bin/sh
set -eu
answerme_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$answerme_root"
answerme_hooks=$(git config --get core.hooksPath || true)
if [ "$answerme_hooks" = '.githooks' ]; then
  printf '%s\n' 'Answer Me hooks are already selected.'
  exit 0
fi
if [ -n "$answerme_hooks" ]; then
  printf '%s\n' "Existing core.hooksPath preserved: $answerme_hooks" >&2
  exit 1
fi
answerme_default_hooks=$(git rev-parse --git-path hooks)
for answerme_hook in "$answerme_default_hooks"/*; do
  case "$answerme_hook" in *.sample) continue ;; esac
  if [ -f "$answerme_hook" ] && [ -x "$answerme_hook" ]; then
    printf '%s\n' "Existing executable hook preserved: $answerme_hook" >&2
    exit 1
  fi
done
git config --local core.hooksPath .githooks
printf '%s\n' 'Enabled .githooks for this repository.'
