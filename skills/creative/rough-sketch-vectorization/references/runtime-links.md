# Shared Codex and Hermes package

Canonical source: `skills/creative/rough-sketch-vectorization/` in the iCloud Drive `agents` repository. Companion persona: `vector-reconstruction-designer/`. Keep the detailed procedure in this package; the persona routes to it.

Installed copies:

- Codex: `~/.agents/skills/rough-sketch-vectorization/`.
- Hermes: `~/.hermes/skills/creative/rough-sketch-vectorization/`.

From the agents repository, inspect a publisher preview, then apply its exact returned hash with the same selection:

```sh
python3 scripts/sync_portable_skills.py --skill rough-sketch-vectorization --plan
python3 scripts/sync_portable_skills.py --skill rough-sketch-vectorization --apply PLAN_HASH
python3 scripts/sync_portable_skills.py --skill rough-sketch-vectorization --check
```

The publisher maintains runtime copies and Hermes ownership locks. Do not hand-edit those copies. Follow the repository README for persona compilation and Codex persona mirroring; preserve existing runtime configuration and memories.

Invoke `$rough-sketch-vectorization` in Codex or `/rough-sketch-vectorization` in Hermes. The companion can be launched with `agent-run vector-reconstruction-designer`; `--dry-run` inspects its configuration without starting a session. A new chat may be needed for discovery metadata to refresh.
