# Triage Labels

Use these canonical role strings in the issue file's `Status:` line.

| Canonical role | Tracker value | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info` | `needs-info` | Waiting on reporter for more information |
| `ready-for-agent` | `ready-for-agent` | Fully specified, ready for an autonomous agent |
| `ready-for-human` | `ready-for-human` | Requires human implementation |
| `wontfix` | `wontfix` | Will not be actioned |

When a skill mentions a triage role, use its corresponding tracker value.
Edit the tracker-value column to change this repo's vocabulary.

Wayfinder lifecycle statuses are defined separately in `docs/agents/issue-tracker.md`.
