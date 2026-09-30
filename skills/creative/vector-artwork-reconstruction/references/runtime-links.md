# Shared source and runtime links

Canonical procedure: `skills/creative/vector-artwork-reconstruction/` in the user's iCloud Drive `agents` repository.

Canonical companion persona: `vector-reconstruction-designer/` in that repository. Its `hermes_skills` metadata and persona instructions name this procedure. This package's `metadata.companion-agent` points back to that persona.

Installed procedure copies:
- Codex: `~/.agents/skills/vector-artwork-reconstruction/`
- Hermes: `~/.hermes/skills/creative/vector-artwork-reconstruction/`

Installed companion:
- Codex persona mirror: `~/.agents/skills/vector-reconstruction-designer/`
- Hermes profile: `~/.hermes/profiles/vector-reconstruction-designer/`

Use the repository's existing synchronization, rather than separate hand-edited runtime versions. These are synchronized copies, not live filesystem symlinks.

After editing the canonical procedure, run from the agents repository:

```sh
python3 scripts/sync_portable_skills.py --skill vector-artwork-reconstruction
python3 scripts/sync_portable_skills.py --skill vector-artwork-reconstruction --check
```

For future persona edits, follow the repository README's profile compilation and Codex mirroring workflow. The Hermes profile links to the shared Hermes skills library, so procedure updates need no profile rebuild.

Invoke the procedure as `$vector-artwork-reconstruction` in Codex, or load it by name in Hermes. Launch the companion with `agent-run vector-reconstruction-designer`. Use `agent-run vector-reconstruction-designer --dry-run` to inspect launch configuration without starting a session.
