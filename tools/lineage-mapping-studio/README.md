# Lineage Mapping Studio

This local Vue tool visualizes lineage evidence produced by `lineage-audit`.
It is a review surface, not a source-of-truth database and not a runtime
configuration editor.

The checked-in `inputs/` and `outputs/` directories are empty. Import a
reviewed evidence bundle from a private or temporary workspace, then discard
the generated bundle after review.

```bash
pnpm install
pnpm build
```
