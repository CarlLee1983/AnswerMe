# Issue tracker: Local Markdown

Issues and specs for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`.
- The spec is `.scratch/<feature-slug>/spec.md`.
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file.
- Triage state is recorded as a `Status:` line near the top of each issue file. Use the role strings in `docs/agents/triage-labels.md`.
- Comments and conversation history append to the bottom of the file under a `## Comments` heading.

## When a skill says "publish to the issue tracker"

Create the spec or individual issue files at the paths above, creating directories as needed.

## When a skill says "fetch the relevant ticket"

Read the referenced file. If given only an issue number, resolve it within the relevant feature directory; ask for the feature if ambiguous.

## Wayfinding operations

Used by `/wayfinder`. The map is a file with one child file per ticket. Wayfinder tickets use the lifecycle statuses below instead of triage statuses.

- **Map**: `.scratch/<effort>/map.md`, holding Notes, Decisions-so-far, and Fog.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records `research`, `prototype`, `grilling`, or `task`. A `Status:` line records `open`, `claimed`, or `resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every listed ticket is `resolved`.
- **Frontier**: scan the effort's issues for open, unblocked tickets; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under `## Answer`, set `Status: resolved`, then append a brief summary and relative link to the map's Decisions-so-far.
