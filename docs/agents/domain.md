# Domain Docs

This repo uses a single-context domain documentation layout.

## Before exploring, read these

- Root `CONTEXT.md`: domain terms and their definitions.
- Relevant ADRs under `docs/adr/`: decisions affecting the area being explored.

If these files do not exist, proceed silently. Domain documentation is created lazily by `/domain-modeling` when terms or decisions are resolved.

## File structure

- `CONTEXT.md`
- `docs/adr/`

## Use the glossary's vocabulary

Use the terms defined in `CONTEXT.md` when naming domain concepts in issue titles, proposals, hypotheses, and tests. Respect any synonyms the glossary explicitly avoids.

If a concept is missing, reconsider whether it belongs to the domain; record genuine vocabulary gaps for `/domain-modeling`.

## Flag ADR conflicts

Explicitly identify any proposal that contradicts an existing ADR, naming the ADR and explaining why the decision should be reconsidered.
