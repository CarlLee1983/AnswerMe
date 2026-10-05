## Agent skills

### Issue tracker

Issues and specs live in `.scratch/<feature>/`. Before issue or spec operations, read `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage roles. Before triaging or setting triage status, read `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `CONTEXT.md` and `docs/adr/`. Before exploring the codebase, read `docs/agents/domain.md`.

### Validation

Before changing skills, checks, or hooks, read [docs/checks.md](docs/checks.md) for the check commands, staged-file guard, and behavioral evaluation boundary.

### Releases

Before drafting a release or tag message, read [docs/release.md](docs/release.md). Agents draft the tag message and run the release check; only the maintainer pushes tags or creates GitHub Releases.
