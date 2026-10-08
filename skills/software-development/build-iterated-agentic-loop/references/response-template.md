# Final response / PR body

Use the repository's required PR template when present. Otherwise customize this compact shape for the actual task:

```markdown
[One sentence: what problem was addressed and resulting behavior, or why no change was eligible.]

## Changes

| Target | Change | Evidence |
|---|---|---|
| [file/component] | [before → after] | [production source or measured finding] |

## Validation

- [Exact command]: [actual result].
- [Before/after measurement when relevant].

## Remaining work

[Only material limits, skipped candidates, or manual checks; omit when empty.]
```

For a migration, report fixed/skipped counts with reasons. For generated artifacts, list created/updated results. For a refactor, identify the preserved contract. Keep the report proportional to the diff and do not include raw tool logs or assert checks that did not run.
