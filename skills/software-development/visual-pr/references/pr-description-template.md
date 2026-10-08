# PR description template

Honor a repository's own template first. Otherwise use this shape, replacing every placeholder and omitting irrelevant views:

````markdown
[Optional verified ticket or design link]

## Why the change

[One sentence describing the problem and resulting behavior.]

## Special things to note

- [1–3 compatibility, migration, or reviewer notes; None if empty.]

## Change outline

[One short sentence introducing the structural view.]

```diff
 on(save)
-  write content
+  skip unchanged content
+  write changed content
+  invalidate cache
```

## Validation

[Actual checks and outcomes, plus any remaining manual verification.]
````

The outline above is illustrative, not a claim about the current PR. Choose a component tree, file tree, contract/type shape, or call flow when it explains the diff better. Keep the description proportional to the change.
