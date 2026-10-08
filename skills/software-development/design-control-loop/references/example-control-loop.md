# Example: narrowing application-internal React props

This is a hypothetical design, not a required toolchain or measured result.

- **Set point:** internal component types express the supported production states; public library contracts are excluded from automatic breaking changes.
- **Sensor:** a repository AST/search command reports optional props and their production call sites. Search findings are candidates, not proof that a prop is redundant.
- **Controller:** select one internal component whose consumers are inspectable; skip externally consumed interfaces and ambiguous spreads. Load standing exclusions before selecting.
- **Actuator:** Codex or Hermes uses `narrow-react-prop-types`, makes the justified narrowing, and updates child variants and fixtures.
- **Validation:** package and consumer typechecks, relevant component tests, and a second sensor pass. Do not accept a cast or disabled check as proof.
- **Disturbances:** teammates introduce new consumers or loading states. Rebase/revalidate according to the repository policy; never force-push over others' changes.
- **Optional regression gate:** report newly widened props on PRs, initially advisory until false positives are understood.
- **Feedback:** a reviewed correction about externally consumed components becomes a scope exclusion for future selection; PR-specific requests stay with that PR.
- **Flow control:** one open PR for this loop. Both manual and scheduled runs obey the bound unless the operator deliberately overrides it.

A local trial records the candidates found, why this target was selected, the actual type/behavior diff, and the validation results. The recurring workflow is connected only after these local pieces have been exercised.
